from app.schemas.legacy import (
    CaseBase, CaseCreate, CaseUpdate, CaseResponse, CasesListResponse,
    TraceLogBase, TraceLogCreate, TraceLogResponse, TraceLogListResponse,
    DocumentUpload, DocumentResponse, DocumentsListResponse,
    RagQueryRequest, SourceCitation, RagQueryResponse, VectorSearchResult,
    SemanticSearchResponse, RagStatsResponse
)
from app.schemas.document import (
    DocumentMetadataInput,
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDetailResponse,
    DocumentVersionResponse,
    ExtractedTextResponse,
    DocumentChunkResponse,
    DocumentChunkListResponse
)
