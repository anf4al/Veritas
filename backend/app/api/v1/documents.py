import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.auth.dependencies import get_current_user, require_permission, verify_tenant_access
from backend.app.auth.permissions import Permission, check_document_access
from backend.app.models.user import User
from backend.app.models.document import Document, Chunk
from backend.app.models.audit import AuditEvent
from backend.app.schemas.document import DocumentOut, ChunkOut, IngestResponse
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.retrieval.vector_store import get_vector_store
from backend.app.observability.cache import get_cache

router = APIRouter(prefix="/documents", tags=["Documents & Ingestion"])

@router.get("", response_model=List[DocumentOut])
def list_documents(
    company_id: str,
    department: Optional[str] = None,
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List authorized documents within a company."""
    verify_tenant_access(current_user, company_id, db)

    query = db.query(Document).filter(Document.company_id == company_id)
    if department:
        query = query.filter(Document.department == department)
    if document_type:
        query = query.filter(Document.document_type == document_type)

    docs = query.order_by(Document.created_at.desc()).all()

    # Filter by user role access
    authorized_docs = []
    for d in docs:
        if check_document_access(
            role=current_user.role,
            doc_department=d.department,
            doc_confidentiality=d.confidentiality,
            doc_type=d.document_type,
            title=d.title
        ):
            chunk_cnt = db.query(Chunk).filter(Chunk.document_id == d.id).count()
            has_file = bool(d.storage_path and Path(d.storage_path).exists())
            authorized_docs.append(DocumentOut(
                id=d.id,
                company_id=d.company_id,
                title=d.title,
                filename=d.filename,
                document_type=d.document_type,
                department=d.department,
                version=d.version,
                effective_date=d.effective_date,
                status=d.status,
                confidentiality=d.confidentiality,
                source=d.source,
                storage_path=d.storage_path,
                has_file=has_file,
                created_at=d.created_at,
                chunk_count=chunk_cnt
            ))

    return authorized_docs

@router.get("/{document_id}/chunks", response_model=List[ChunkOut])
def get_document_chunks(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve chunks for an authorized document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    verify_tenant_access(current_user, doc.company_id, db)

    if not check_document_access(
        role=current_user.role,
        doc_department=doc.department,
        doc_confidentiality=doc.confidentiality,
        doc_type=doc.document_type,
        title=doc.title
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")

    chunks = db.query(Chunk).filter(Chunk.document_id == doc.id).order_by(Chunk.chunk_index).all()
    return chunks

@router.post("/upload", response_model=IngestResponse)
async def upload_document(
    company_id: str = Form(...),
    title: Optional[str] = Form(None),
    department: str = Form("General"),
    document_type: str = Form("policy"),
    version: str = Form("1.0"),
    effective_date: Optional[str] = Form(None),
    confidentiality: str = Form("internal"),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.DOCUMENT_UPLOAD)),
    db: Session = Depends(get_db)
):
    """Upload and ingest a physical document into company knowledge base."""
    verify_tenant_access(current_user, company_id, db)

    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = settings.UPLOADS_DIR / f"{company_id}_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        pipeline = IngestionPipeline(db=db)
        doc = pipeline.ingest_file(
            file_path=temp_path,
            company_id=company_id,
            title=title or file.filename.rsplit(".", 1)[0].replace("_", " ").title(),
            department=department,
            document_type=document_type,
            version=version,
            effective_date=effective_date,
            confidentiality=confidentiality,
            user_id=current_user.id
        )

        # Invalidate retrieval cache for this tenant
        get_cache().invalidate_tenant(company_id)

        # Persist physical file permanently in tenant storage directory
        storage_company_dir = settings.STORAGE_DIR / "documents" / company_id
        storage_company_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename).suffix or ".pdf"
        dest_path = storage_company_dir / f"{doc.id}{ext}"
        shutil.copyfile(temp_path, dest_path)
        doc.storage_path = str(dest_path.resolve())
        db.commit()
        db.refresh(doc)

        chunks_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()

        return IngestResponse(
            document_id=doc.id,
            title=doc.title,
            chunks_created=chunks_count,
            status="indexed",
            message=f"Document '{doc.title}' successfully parsed, chunked, and indexed."
        )
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(require_permission(Permission.DOCUMENT_DELETE)),
    db: Session = Depends(get_db)
):
    """Delete document and its associated chunks/vectors."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    verify_tenant_access(current_user, doc.company_id, db)

    # Delete vectors
    get_vector_store().delete_document(doc.id)
    # Invalidate cache
    get_cache().invalidate_tenant(doc.company_id)

    # Delete physical file from disk if present
    if doc.storage_path:
        stored_file = Path(doc.storage_path)
        if stored_file.exists():
            stored_file.unlink(missing_ok=True)

    db.delete(doc)
    db.commit()

    return {"status": "success", "message": f"Document '{doc.title}' deleted."}

@router.get("/{document_id}/file")
def get_document_file(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream or serve physical document PDF for authorized users."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    verify_tenant_access(current_user, doc.company_id, db)

    if not check_document_access(
        role=current_user.role,
        doc_department=doc.department,
        doc_confidentiality=doc.confidentiality,
        doc_type=doc.document_type,
        title=doc.title
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")

    if not doc.storage_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file not available for this document.")

    file_path = Path(doc.storage_path).resolve()
    # Security: Directory traversal prevention
    storage_root = settings.STORAGE_DIR.resolve()
    try:
        file_path.relative_to(storage_root)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to file path is forbidden.")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file does not exist on disk.")

    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "application/octet-stream"
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=f"{doc.title}{file_path.suffix}"
    )

