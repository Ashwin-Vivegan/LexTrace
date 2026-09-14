import sys
import platform
from datetime import datetime
from fastapi import APIRouter
from app.services.rag_engine import rag_service

router = APIRouter()

@router.get("/health")
def get_health():
    rag_stats = rag_service.get_stats()
    return {
        "status": "online",
        "service": "Lextrace Python FastAPI RAG Engine",
        "version": "2.4.0",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.platform(),
            "pythonVersion": sys.version,
            "fastapi": True
        },
        "rag": {
            "status": rag_stats.indexStatus,
            "totalDocuments": rag_stats.totalDocuments,
            "totalIndexedChunks": rag_stats.totalIndexedChunks,
            "vectorDimensions": rag_stats.vectorSpaceDimensions,
            "embeddingModel": rag_stats.embeddingModel
        }
    }
