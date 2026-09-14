from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime

ALLOWED_DOCUMENT_TYPES = {"contract", "case_precedent", "regulation", "other"}
ALLOWED_STATUSES = {"current", "superseded", "draft"}

class DocumentMetadataInput(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field("other", description="contract, case_precedent, regulation, or other")
    jurisdiction: Optional[str] = Field(None, max_length=100)
    practice_area: Optional[str] = Field(None, max_length=100)
    client_reference: Optional[str] = Field(None, max_length=100)
    version_number: str = Field("1.0", max_length=20)
    effective_date: Optional[str] = Field(None, max_length=50)
    status: str = Field("current", description="current, superseded, or draft")
    existing_document_id: Optional[str] = Field(None, description="Provide if adding a version to an existing document")

    @field_validator("document_type")
    def validate_doc_type(cls, v):
        v_clean = v.lower().strip()
        if v_clean not in ALLOWED_DOCUMENT_TYPES:
            raise ValueError(f"document_type must be one of: {', '.join(ALLOWED_DOCUMENT_TYPES)}")
        return v_clean

    @field_validator("status")
    def validate_status(cls, v):
        v_clean = v.lower().strip()
        if v_clean not in ALLOWED_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(ALLOWED_STATUSES)}")
        return v_clean

class DocumentUploadResponse(BaseModel):
    document_id: str
    version_id: str
    document_name: str
    document_type: str
    version_number: str
    status: str
    file_type: str
    file_size: int
    text_length: int
    chunk_count: int
    message: str

class DocumentVersionResponse(BaseModel):
    version_id: str
    version_number: str
    status: str
    file_name: str
    file_type: str
    file_size: int
    text_length: int
    chunk_count: int = 0
    effective_date: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListItem(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    jurisdiction: Optional[str] = None
    practice_area: Optional[str] = None
    client_reference: Optional[str] = None
    current_version: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    jurisdiction: Optional[str] = None
    practice_area: Optional[str] = None
    client_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    current_version: Optional[str] = None
    versions: List[DocumentVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ExtractedTextResponse(BaseModel):
    document_id: str
    version_id: str
    text: str

class DocumentChunkResponse(BaseModel):
    chunk_id: str
    chunk_index: int
    section_name: Optional[str] = None
    subsection_name: Optional[str] = None
    page_number: Optional[int] = None
    character_start: Optional[int] = None
    character_end: Optional[int] = None
    content: str

    model_config = ConfigDict(from_attributes=True)

class DocumentChunkListResponse(BaseModel):
    document_id: str
    version_id: str
    total_chunks: int
    page: int
    limit: int
    chunks: List[DocumentChunkResponse]
