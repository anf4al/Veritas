import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.document import Document, Chunk
from backend.app.models.audit import AuditEvent
from backend.app.ingestion.extractor import extract_text_from_file
from backend.app.ingestion.cleaner import clean_extracted_text
from backend.app.ingestion.chunker import chunk_document_text
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.retrieval.vector_store import VectorPayload
from backend.app.retrieval.embeddings import get_embedding_provider

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()

    def ingest_file(
        self,
        file_path: Path,
        company_id: str,
        title: Optional[str] = None,
        department: str = "General",
        document_type: str = "policy",
        version: str = "1.0",
        effective_date: Optional[str] = None,
        confidentiality: str = "internal",
        user_id: Optional[str] = None
    ) -> Document:
        """Ingest a physical file into the database and vector store."""
        filename = file_path.name
        doc_title = title or file_path.stem.replace("_", " ").title()

        # Compute checksum
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                hasher.update(block)
        checksum = hasher.hexdigest()

        # Extract and clean text
        raw_pages = extract_text_from_file(file_path)
        cleaned_pages = [(p, clean_extracted_text(t)) for p, t in raw_pages]

        # Chunk
        chunks = chunk_document_text(cleaned_pages)

        # Create Document record
        doc = Document(
            company_id=company_id,
            title=doc_title,
            filename=filename,
            document_type=document_type,
            department=department,
            version=version,
            effective_date=effective_date,
            status="indexing",
            confidentiality=confidentiality,
            source="upload",
            checksum=checksum
        )
        self.db.add(doc)
        self.db.flush()

        # Create Chunk records
        chunk_models: List[Chunk] = []
        payloads: List[VectorPayload] = []

        chunk_texts = [c.text for c in chunks]
        embeddings = self.embedding_provider.embed_batch(chunk_texts) if chunk_texts else []

        for idx, c in enumerate(chunks):
            emb = embeddings[idx] if idx < len(embeddings) else []
            chunk_rec = Chunk(
                document_id=doc.id,
                company_id=company_id,
                chunk_index=c.chunk_index,
                text=c.text,
                page=c.page,
                section=c.section,
                metadata_json=c.metadata_json
            )
            self.db.add(chunk_rec)
            self.db.flush()
            chunk_models.append(chunk_rec)

            payloads.append(VectorPayload(
                chunk_id=chunk_rec.id,
                document_id=doc.id,
                tenant_id=company_id,
                text=c.text,
                title=doc_title,
                document_type=document_type,
                department=department,
                version=version,
                effective_date=effective_date,
                confidentiality=confidentiality,
                page=c.page,
                section=c.section,
                vector=emb,
                metadata_json=c.metadata_json
            ))

        # Index into Tenant Knowledge Store
        tenant_store = TenantKnowledgeStore(tenant_id=company_id)
        tenant_store.index_document_chunks(payloads)

        doc.status = "indexed"

        # Log audit event
        audit = AuditEvent(
            company_id=company_id,
            user_id=user_id,
            action="document_ingest",
            details={
                "document_id": doc.id,
                "title": doc_title,
                "chunks_count": len(chunks)
            }
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(doc)
        return doc
