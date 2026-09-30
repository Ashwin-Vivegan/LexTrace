import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Mock the embedding provider and vector store in the semantic search router
# to avoid loading the real model and writing to real disk during fast unit tests.
from app.services.semantic_search import SemanticSearchService
from app.routers.semantic_search import get_semantic_search_service

class FakeEmbeddingProvider:
    @property
    def dimension(self):
        return 3
    def embed_text(self, text):
        return [0.1, 0.2, 0.3]
    def embed_texts(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]

class FakeVectorStore:
    def __init__(self):
        self._count = 0
        self.mapping = []
    
    def add_vectors(self, chunk_ids, vectors):
        self.mapping.extend(chunk_ids)
        self._count += len(chunk_ids)
        
    def search(self, query_vector, top_k=5):
        if self._count == 0:
            return []
        # Return a fake match for the first indexed chunk if any
        return [(self.mapping[0], 0.99)] if self.mapping else []
        
    def clear(self):
        self._count = 0
        self.mapping = []
        
    def save(self):
        pass
        
    def load(self):
        pass
        
    @property
    def count(self):
        return self._count

def override_get_semantic_search_service():
    provider = FakeEmbeddingProvider()
    store = FakeVectorStore()
    return SemanticSearchService(embedding_provider=provider, vector_store=store)

app.dependency_overrides[get_semantic_search_service] = override_get_semantic_search_service

client = TestClient(app)

def test_semantic_search_empty_index():
    response = client.post("/api/search/semantic", json={"query": "test query", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert data["results"] == []

def test_index_status():
    response = client.get("/api/search/index/status")
    assert response.status_code == 200
    data = response.json()
    assert "dimension" in data
    assert data["dimension"] > 0      # real or fake provider both return a positive int
    assert "vector_count" in data
    assert "is_ready" in data
