"""
LexTrace canonical schema package.

All Pydantic request/response schemas for the LexTrace backend are
defined here and re-exported from this single package.

Sub-modules:
  app.schemas.document — Document, Version, and Chunk Pydantic models
  app.schemas.legacy   — Case, Trace, and RAG schemas (in-memory layer)
  app.schemas.search   — Semantic Search models

The root-level app/schemas.py has been removed. Import from
`app.schemas` or directly from the appropriate sub-module.
"""

from app.schemas.legacy import (
    CaseBase, CaseCreate, CaseUpdate, CaseResponse, CasesListResponse,
    TraceLogBase, TraceLogCreate, TraceLogResponse, TraceLogListResponse,
    DocumentUpload, DocumentResponse, DocumentsListResponse,
    RagQueryRequest, SourceCitation, RagQueryResponse, VectorSearchResult,
    SemanticSearchResponse as LegacySemanticSearchResponse, RagStatsResponse
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
from app.schemas.search import (
    SemanticSearchRequest,
    SemanticSearchResultItem,
    SemanticSearchResponse,
    IndexStatusResponse
)
