import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False, index=True)  # policy, contract, report, handbook, sop, manual
    department = Column(String(100), nullable=False, index=True)     # HR, Procurement, Legal, Security, Operations, etc.
    version = Column(String(50), nullable=False, default="1.0")
    effective_date = Column(String(50), nullable=True)               # e.g. "2026-01-01"
    status = Column(String(50), nullable=False, default="indexed")   # pending, indexing, indexed, failed, outdated
    confidentiality = Column(String(50), nullable=False, default="internal") # public, internal, confidential, restricted
    source = Column(String(255), nullable=True)                      # seed, upload, manual
    checksum = Column(String(64), nullable=True)                     # sha256
    storage_path = Column(String(500), nullable=True)                 # Persistent path to stored PDF/binary
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page = Column(Integer, nullable=True, default=1)
    section = Column(String(255), nullable=True)
    metadata_json = Column(JSON, nullable=True, default=dict)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    company = relationship("Company", back_populates="chunks")
