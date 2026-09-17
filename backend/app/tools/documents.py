from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.document import Document, Chunk
from backend.app.tools.base import EnterpriseTool
from backend.app.auth.permissions import check_document_access

class GetDocumentTool(EnterpriseTool):
    name = "get_document"
    description = "Retrieve the full authorized text and metadata of a specific document by its title or ID."
    parameters_schema = {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The unique document ID (optional if title is provided)."
            },
            "title": {
                "type": "string",
                "description": "The document title or partial title."
            }
        }
    }

    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        doc_id = kwargs.get("document_id")
        title = kwargs.get("title")

        query = db.query(Document).filter(Document.company_id == tenant_id)
        if doc_id:
            query = query.filter(Document.id == doc_id)
        elif title:
            query = query.filter(Document.title.ilike(f"%{title}%"))
        else:
            return {"error": "Either document_id or title must be provided."}

        doc = query.first()
        if not doc:
            return {"error": "Document not found in active company."}

        # RBAC Check
        if not check_document_access(
            role=user.role,
            doc_department=doc.department,
            doc_confidentiality=doc.confidentiality,
            doc_type=doc.document_type,
            title=doc.title
        ):
            return {"error": "Access denied: your role is not authorized to inspect this document."}

        # Load chunks
        chunks = db.query(Chunk).filter(Chunk.document_id == doc.id).order_by(Chunk.chunk_index).all()
        full_text = "\n\n".join([c.text for c in chunks])

        return {
            "document_id": doc.id,
            "title": doc.title,
            "department": doc.department,
            "document_type": doc.document_type,
            "version": doc.version,
            "effective_date": doc.effective_date,
            "confidentiality": doc.confidentiality,
            "total_chunks": len(chunks),
            "content": full_text
        }

class CompareDocumentsTool(EnterpriseTool):
    name = "compare_documents"
    description = (
        "Compare two enterprise documents or policy versions side-by-side to identify "
        "changes, additions, removals, and updated thresholds."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "title_a": {
                "type": "string",
                "description": "Title or keyword of the first document (e.g. 2025 version)."
            },
            "title_b": {
                "type": "string",
                "description": "Title or keyword of the second document (e.g. 2026 version)."
            }
        },
        "required": ["title_a", "title_b"]
    }

    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        title_a = kwargs.get("title_a", "").strip()
        title_b = kwargs.get("title_b", "").strip()

        doc_a = db.query(Document).filter(
            Document.company_id == tenant_id,
            Document.title.ilike(f"%{title_a}%")
        ).first()

        doc_b = db.query(Document).filter(
            Document.company_id == tenant_id,
            Document.title.ilike(f"%{title_b}%")
        ).first()

        if not doc_a or not doc_b:
            return {
                "error": f"Could not locate both documents for comparison (found doc_a: {bool(doc_a)}, found doc_b: {bool(doc_b)})."
            }

        # Check access for both
        for d in (doc_a, doc_b):
            if not check_document_access(user.role, d.department, d.confidentiality, d.document_type, d.title):
                return {"error": f"Access denied for document: '{d.title}'."}

        chunks_a = db.query(Chunk).filter(Chunk.document_id == doc_a.id).order_by(Chunk.chunk_index).all()
        chunks_b = db.query(Chunk).filter(Chunk.document_id == doc_b.id).order_by(Chunk.chunk_index).all()

        text_a = "\n".join([c.text for c in chunks_a])
        text_b = "\n".join([c.text for c in chunks_b])

        return {
            "document_a": {
                "id": doc_a.id,
                "title": doc_a.title,
                "version": doc_a.version,
                "effective_date": doc_a.effective_date,
                "text_sample": text_a[:1500]
            },
            "document_b": {
                "id": doc_b.id,
                "title": doc_b.title,
                "version": doc_b.version,
                "effective_date": doc_b.effective_date,
                "text_sample": text_b[:1500]
            },
            "comparison_summary": f"Comparing '{doc_a.title}' (v{doc_a.version}) with '{doc_b.title}' (v{doc_b.version})."
        }

class GetPolicyVersionsTool(EnterpriseTool):
    name = "get_policy_versions"
    description = "List all historical and current versions of an organizational policy or guideline."
    parameters_schema = {
        "type": "object",
        "properties": {
            "policy_name": {
                "type": "string",
                "description": "Name or topic of the policy (e.g. 'Procurement Policy', 'WFH Policy')."
            }
        },
        "required": ["policy_name"]
    }

    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        policy_name = kwargs.get("policy_name", "").strip()

        docs = db.query(Document).filter(
            Document.company_id == tenant_id,
            Document.title.ilike(f"%{policy_name}%")
        ).order_by(Document.created_at.desc()).all()

        authorized_docs = []
        for d in docs:
            if check_document_access(user.role, d.department, d.confidentiality, d.document_type, d.title):
                authorized_docs.append({
                    "id": d.id,
                    "title": d.title,
                    "version": d.version,
                    "effective_date": d.effective_date,
                    "department": d.department,
                    "status": d.status,
                    "confidentiality": d.confidentiality
                })

        return {
            "policy_name": policy_name,
            "total_versions_found": len(authorized_docs),
            "versions": authorized_docs
        }

