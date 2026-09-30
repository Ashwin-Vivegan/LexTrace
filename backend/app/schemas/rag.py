from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Legal question or query to be answered using retrieved evidence")
    top_k: int = Field(5, ge=1, le=50, description="Number of candidate evidence chunks to retrieve for context")

class CitationItem(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    document_type: str
    jurisdiction: Optional[str] = None
    practice_area: Optional[str] = None
    version_id: str
    version_number: str
    section_name: Optional[str] = None
    subsection_name: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: int
    content: str

class RAGMetadata(BaseModel):
    retrieval_mode: str = "hybrid"
    chunks_retrieved: int
    chunks_used: int
    model: str
    latency_ms: float

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[CitationItem]
    retrieved_chunks: List[Dict[str, Any]]
    metadata: RAGMetadata
