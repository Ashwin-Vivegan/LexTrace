from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SearchMode(str, Enum):
    semantic = "semantic"
    keyword = "keyword"
    hybrid = "hybrid"

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=50)

class HybridSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=50)
    semantic_weight: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    keyword_weight: Optional[float] = Field(0.3, ge=0.0, le=1.0)

class UnifiedSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=50)
    mode: SearchMode = Field(default=SearchMode.hybrid)
    semantic_weight: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    keyword_weight: Optional[float] = Field(0.3, ge=0.0, le=1.0)

class SearchResultItem(BaseModel):
    chunk_id: str
    score: float
    retrieval_type: str
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
    
# Keep backward compatibility
class SemanticSearchResultItem(BaseModel):
    chunk_id: str
    similarity_score: float
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

class SemanticSearchResponse(BaseModel):
    query: str
    results: List[SemanticSearchResultItem]

class UnifiedSearchResponse(BaseModel):
    query: str
    mode: str
    result_count: int
    results: List[SearchResultItem]

class IndexStatusResponse(BaseModel):
    vector_count: int
    dimension: int
    is_ready: bool
    fts5_count: int = 0
    fts5_ready: bool = False
