from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.routers.semantic_search import get_hybrid_search_service
from app.services.hybrid_search import HybridSearchService
from app.services.rag_service import RAGService
from app.services.llm_provider import GroqLLMProvider

router = APIRouter(prefix="/rag", tags=["RAG Research Assistant"])

_groq_provider = GroqLLMProvider()

def get_rag_service(
    hybrid_service: HybridSearchService = Depends(get_hybrid_search_service)
) -> RAGService:
    return RAGService(hybrid_search_service=hybrid_service, llm_provider=_groq_provider)


@router.post("/ask", response_model=RAGQueryResponse)
def ask_rag_ai(
    payload: RAGQueryRequest,
    db: Session = Depends(get_db),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Executes RAG AI workflow: M4 Hybrid Search + Context Construction + Groq LLM Generation + Database Source Citations.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty or whitespace-only."
        )

    try:
        result = rag_service.ask(db, query=payload.query, top_k=payload.top_k)
        return RAGQueryResponse(**result)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
