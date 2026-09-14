from fastapi import APIRouter, status
from app.services.rag_engine import rag_service
from app.schemas import (
    RagQueryRequest, RagQueryResponse, RagStatsResponse, SemanticSearchResponse, VectorSearchResult
)

router = APIRouter(prefix="/rag", tags=["RAG AI Engine"])

@router.post("/ask", response_model=RagQueryResponse)
def ask_rag_ai(payload: RagQueryRequest):
    """Executes RAG AI workflow: Vector Search + Augmented Context Generation + Citation Extraction."""
    return rag_service.ask(
        query=payload.query,
        case_id_filter=payload.caseId,
        top_k=payload.topK or 3,
        min_similarity=payload.minSimilarity or 0.05
    )

@router.post("/semantic-search", response_model=SemanticSearchResponse)
def semantic_search(payload: RagQueryRequest):
    """Performs raw vector similarity search against document chunks."""
    matches = rag_service.search_vectors(
        query=payload.query,
        case_id_filter=payload.caseId,
        top_k=payload.topK or 5,
        min_similarity=payload.minSimilarity or 0.01
    )
    
    results = [
        VectorSearchResult(
            chunkId=chunk.chunk_id,
            documentId=chunk.document_id,
            documentName=chunk.document_name,
            caseId=chunk.case_id,
            snippet=chunk.text,
            similarityScore=round(score * 100, 2)
        )
        for chunk, score in matches
    ]
    
    return {
        "success": True,
        "query": payload.query,
        "count": len(results),
        "results": results
    }

@router.post("/ingest")
def reindex_documents():
    """Forces re-chunking and vector indexing across all documents."""
    rag_service.reindex_all_documents()
    return {
        "success": True,
        "message": "RAG vector space re-indexed successfully.",
        "stats": rag_service.get_stats()
    }

@router.get("/stats", response_model=RagStatsResponse)
def get_rag_stats():
    """Returns vector store metrics and index status."""
    return rag_service.get_stats()
