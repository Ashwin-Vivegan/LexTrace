import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    HybridSearchRequest,
    UnifiedSearchRequest,
    UnifiedSearchResponse,
    IndexStatusResponse,
    SearchMode
)
from app.services.embeddings.local import LocalSentenceTransformerProvider
from app.services.vector_store.faiss_store import FaissVectorStore
from app.services.semantic_search import SemanticSearchService
from app.services.keyword_search import KeywordSearchService
from app.services.hybrid_search import HybridSearchService

router = APIRouter(prefix="/search", tags=["Search"])

# Path to store FAISS index
PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_store")

_embedding_provider = LocalSentenceTransformerProvider()
_vector_store = None
_keyword_service = KeywordSearchService()

def get_semantic_search_service() -> SemanticSearchService:
    global _vector_store
    if _vector_store is None:
        dim = _embedding_provider.dimension
        _vector_store = FaissVectorStore(persist_dir=PERSIST_DIR, dimension=dim)
    return SemanticSearchService(embedding_provider=_embedding_provider, vector_store=_vector_store)

def get_keyword_search_service() -> KeywordSearchService:
    return _keyword_service

def get_hybrid_search_service(
    sem_service: SemanticSearchService = Depends(get_semantic_search_service),
    kw_service: KeywordSearchService = Depends(get_keyword_search_service)
) -> HybridSearchService:
    return HybridSearchService(semantic_service=sem_service, keyword_service=kw_service)


@router.post("/semantic", response_model=SemanticSearchResponse)
def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
    search_service: SemanticSearchService = Depends(get_semantic_search_service)
):
    """
    Semantic-only vector search endpoint using FAISS and Sentence Transformers.
    Preserved for backward compatibility.
    """
    try:
        results = search_service.search(db, request.query, request.top_k)
        return SemanticSearchResponse(query=request.query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hybrid", response_model=UnifiedSearchResponse)
def hybrid_search(
    request: HybridSearchRequest,
    db: Session = Depends(get_db),
    hybrid_service: HybridSearchService = Depends(get_hybrid_search_service)
):
    """
    Dedicated Hybrid Search endpoint combining FAISS vector search and SQLite FTS5 keyword search.
    """
    try:
        results = hybrid_service.search(
            db=db,
            query=request.query,
            top_k=request.top_k,
            mode=SearchMode.hybrid,
            semantic_weight=request.semantic_weight,
            keyword_weight=request.keyword_weight
        )
        return UnifiedSearchResponse(
            query=request.query,
            mode="hybrid",
            result_count=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=UnifiedSearchResponse)
def unified_search(
    request: UnifiedSearchRequest,
    db: Session = Depends(get_db),
    hybrid_service: HybridSearchService = Depends(get_hybrid_search_service)
):
    """
    Unified search endpoint supporting mode selection: 'hybrid', 'semantic', or 'keyword'.
    """
    try:
        results = hybrid_service.search(
            db=db,
            query=request.query,
            top_k=request.top_k,
            mode=request.mode,
            semantic_weight=request.semantic_weight,
            keyword_weight=request.keyword_weight
        )
        return UnifiedSearchResponse(
            query=request.query,
            mode=request.mode.value,
            result_count=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index/status", response_model=IndexStatusResponse)
def get_index_status(
    db: Session = Depends(get_db),
    sem_service: SemanticSearchService = Depends(get_semantic_search_service),
    kw_service: KeywordSearchService = Depends(get_keyword_search_service)
):
    """
    Returns index counts and readiness status for both FAISS vector store and SQLite FTS5 keyword store.
    """
    sem_status = sem_service.get_status()
    kw_status = kw_service.get_status(db)
    
    return IndexStatusResponse(
        vector_count=sem_status["vector_count"],
        dimension=sem_status["dimension"],
        is_ready=sem_status["is_ready"],
        fts5_count=kw_status["fts5_count"],
        fts5_ready=kw_status["fts5_ready"]
    )

@router.post("/documents/{document_id}/versions/{version_id}/index")
def index_document_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    sem_service: SemanticSearchService = Depends(get_semantic_search_service),
    kw_service: KeywordSearchService = Depends(get_keyword_search_service)
):
    """
    Indexes a specific DocumentVersion into both FAISS vector store and SQLite FTS5 keyword index.
    """
    try:
        # Index in FAISS
        faiss_indexed = sem_service.index_document_version(db, version_id)
        
        # Index in FTS5
        from app.db.models import DocumentChunk
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_version_id == version_id).all()
        fts5_indexed = kw_service.index_chunks(db, chunks)
        
        return {
            "message": f"Successfully indexed version {version_id} in FAISS and FTS5.",
            "faiss_count": faiss_indexed,
            "fts5_count": fts5_indexed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-keyword-index")
def rebuild_keyword_index(
    db: Session = Depends(get_db),
    kw_service: KeywordSearchService = Depends(get_keyword_search_service)
):
    """
    Rebuilds only the SQLite FTS5 keyword index from active DocumentChunk records.
    """
    try:
        total_indexed = kw_service.rebuild_index(db)
        return {
            "message": f"SQLite FTS5 keyword index rebuilt successfully with {total_indexed} chunks.",
            "indexed_count": total_indexed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-index")
def rebuild_index(
    db: Session = Depends(get_db),
    sem_service: SemanticSearchService = Depends(get_semantic_search_service),
    kw_service: KeywordSearchService = Depends(get_keyword_search_service)
):
    """
    Rebuilds both FAISS vector index and SQLite FTS5 keyword index from active DocumentChunk records.
    """
    try:
        faiss_count = sem_service.rebuild_index(db)
        fts5_count = kw_service.rebuild_index(db)
        return {
            "message": f"Both indices rebuilt successfully. FAISS vectors: {faiss_count}, FTS5 chunks: {fts5_count}.",
            "faiss_count": faiss_count,
            "fts5_count": fts5_count,
            "indexed_count": faiss_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
