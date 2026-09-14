from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Document(Base):
    """
    Represents a logical legal document in LexTrace (e.g. Master Services Agreement, Case Precedent).
    A Document can have multiple version snapshots stored in DocumentVersion.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String(50), unique=True, index=True, nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False, default="other") # contract, case_precedent, regulation, other
    jurisdiction = Column(String(100), nullable=True)
    practice_area = Column(String(100), nullable=True)
    client_reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationship to DocumentVersion
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.id.desc()"
    )

class DocumentVersion(Base):
    """
    Represents an immutable version snapshot of a Document (e.g., Version 1.0, Version 2.0).
    Stores physical file location, file size, status, extracted text, and chunks.
    """
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version_id = Column(String(100), unique=True, index=True, nullable=False)
    document_id = Column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    version_number = Column(String(20), nullable=False, default="1.0")
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False) # pdf, docx, txt
    file_size = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)
    effective_date = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="current") # current, superseded, draft
    created_at = Column(DateTime, default=utc_now)

    # Relationship back to Document
    document = relationship("Document", back_populates="versions")
    
    # Relationship to DocumentChunk
    chunks = relationship(
        "DocumentChunk",
        back_populates="document_version",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index.asc()"
    )

class DocumentChunk(Base):
    """
    Represents a searchable sequential text chunk extracted from a specific DocumentVersion.
    Preserves structural metadata (section, subsection, page, offsets) for precise citations.
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chunk_id = Column(String(100), unique=True, index=True, nullable=False)
    document_version_id = Column(String(100), ForeignKey("document_versions.version_id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    section_name = Column(String(255), nullable=True)
    subsection_name = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    character_start = Column(Integer, nullable=True)
    character_end = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationship back to DocumentVersion
    document_version = relationship("DocumentVersion", back_populates="chunks")
