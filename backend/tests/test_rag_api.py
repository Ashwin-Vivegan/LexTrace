import pytest
from unittest.mock import patch, MagicMock
from app.services.rag_service import INSUFFICIENT_EVIDENCE_TEXT

def test_rag_api_empty_query(client):
    response = client.post("/api/rag/ask", json={"query": "", "top_k": 5})
    assert response.status_code in [400, 422]

def test_rag_api_whitespace_query(client):
    response = client.post("/api/rag/ask", json={"query": "    ", "top_k": 5})
    assert response.status_code in [400, 422]

@patch("app.services.llm_provider.GroqLLMProvider.generate_answer")
def test_rag_api_valid_ask(mock_generate, client):
    mock_generate.return_value = "The agreement specifies 30 days notice for termination."
    
    response = client.post("/api/rag/ask", json={"query": "What is the termination notice period?", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "metadata" in data
    assert data["metadata"]["retrieval_mode"] == "hybrid"

@patch("app.services.hybrid_search.HybridSearchService.search")
def test_rag_api_insufficient_evidence(mock_search, client):
    mock_search.return_value = []
    
    response = client.post("/api/rag/ask", json={"query": "What is the submarine policy?", "top_k": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == INSUFFICIENT_EVIDENCE_TEXT
    assert len(data["citations"]) == 0
    assert data["metadata"]["chunks_retrieved"] == 0
