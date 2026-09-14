from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# Case Schemas
class CaseBase(BaseModel):
    title: str
    client: str
    court: Optional[str] = "Standard Jurisdiction"
    type: Optional[str] = "General Legal Trace"
    status: Optional[str] = "In Review"
    riskLevel: Optional[str] = "Medium"
    complianceScore: Optional[int] = 80
    leadCounsel: Optional[str] = "Unassigned"
    summary: Optional[str] = "Legal trace case record."

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    client: Optional[str] = None
    court: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    riskLevel: Optional[str] = None
    complianceScore: Optional[int] = None
    leadCounsel: Optional[str] = None
    summary: Optional[str] = None

class CaseResponse(CaseBase):
    id: str
    lastUpdated: str
    auditCount: int

class CasesListResponse(BaseModel):
    success: bool
    count: int
    data: List[CaseResponse]

# Trace Log Schemas
class TraceLogBase(BaseModel):
    action: str
    caseId: str
    caseTitle: Optional[str] = ""
    actor: Optional[str] = "System AI Engine"
    details: Optional[str] = ""
    hash: Optional[str] = None
    status: Optional[str] = "VERIFIED"

class TraceLogCreate(TraceLogBase):
    pass

class TraceLogResponse(TraceLogBase):
    id: str
    timestamp: str
    hash: str

class TraceLogListResponse(BaseModel):
    success: bool
    count: int
    data: List[TraceLogResponse]

# Document Schemas
class DocumentUpload(BaseModel):
    name: str
    caseId: str
    caseTitle: Optional[str] = ""
    category: Optional[str] = "Legal Contract"
    content: Optional[str] = ""
    fileSize: Optional[str] = "45 KB"

class DocumentResponse(BaseModel):
    id: str
    name: str
    caseId: str
    caseTitle: str
    category: str
    fileSize: str
    uploadDate: str
    indexedChunks: int
    ragStatus: str
    hash: str
    contentPreview: str

class DocumentsListResponse(BaseModel):
    success: bool
    count: int
    data: List[DocumentResponse]

# RAG Schemas
class RagQueryRequest(BaseModel):
    query: str = Field(..., description="The user's question or search query for legal documents")
    caseId: Optional[str] = Field(None, description="Optional Case ID filter")
    topK: Optional[int] = Field(3, description="Number of top document chunks to retrieve")
    minSimilarity: Optional[float] = Field(0.15, description="Minimum similarity threshold")

class SourceCitation(BaseModel):
    documentId: str
    documentName: str
    caseId: str
    caseTitle: str
    chunkId: str
    similarityScore: float
    snippet: str
    category: str

class RagQueryResponse(BaseModel):
    success: bool
    query: str
    answer: str
    confidenceScore: float
    retrievedCount: int
    processingTimeMs: float
    citations: List[SourceCitation]
    usedCaseFilter: Optional[str] = None

class VectorSearchResult(BaseModel):
    chunkId: str
    documentId: str
    documentName: str
    caseId: str
    snippet: str
    similarityScore: float

class SemanticSearchResponse(BaseModel):
    success: bool
    query: str
    count: int
    results: List[VectorSearchResult]

class RagStatsResponse(BaseModel):
    success: bool
    totalDocuments: int
    totalIndexedChunks: int
    vectorSpaceDimensions: int
    embeddingModel: str
    indexStatus: str
    lastIngestTime: str
