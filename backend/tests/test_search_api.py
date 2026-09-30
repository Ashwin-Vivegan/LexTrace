import pytest

def test_semantic_search_api_endpoint(client):
    response = client.post("/api/search/semantic", json={"query": "test query", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data

def test_hybrid_search_api_endpoint(client):
    response = client.post("/api/search/hybrid", json={"query": "termination agreement", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "hybrid"
    assert "results" in data

def test_unified_search_api_endpoint(client):
    response = client.post("/api/search", json={"query": "governing law", "top_k": 3, "mode": "hybrid"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "hybrid"
    assert "results" in data

def test_index_status_api_endpoint(client):
    response = client.get("/api/search/index/status")
    assert response.status_code == 200
    data = response.json()
    assert "vector_count" in data
    assert "fts5_count" in data
    assert "fts5_ready" in data

def test_rebuild_keyword_index_api_endpoint(client):
    response = client.post("/api/search/rebuild-keyword-index")
    assert response.status_code == 200
    data = response.json()
    assert "indexed_count" in data
