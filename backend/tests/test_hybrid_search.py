import pytest
from app.services.hybrid_search import HybridSearchService
from app.services.keyword_search import KeywordSearchService
from app.services.semantic_search import SemanticSearchService
from app.services.embeddings.local import LocalSentenceTransformerProvider
from app.services.vector_store.faiss_store import FaissVectorStore
from app.schemas.search import SearchMode
from app.db.models import Document, DocumentVersion, DocumentChunk

@pytest.fixture
def hybrid_components(tmp_path, db):
    embed_provider = LocalSentenceTransformerProvider()
    vector_store = FaissVectorStore(persist_dir=str(tmp_path), dimension=embed_provider.dimension)
    sem_service = SemanticSearchService(embedding_provider=embed_provider, vector_store=vector_store)
    kw_service = KeywordSearchService()
    
    # Populate test document
    doc = Document(document_id="DOC-HYB-01", document_name="Hybrid Test Agreement", document_type="contract")
    db.add(doc)
    db.flush()

    ver = DocumentVersion(
        version_id="VER-HYB-01",
        document_id="DOC-HYB-01",
        version_number="1.0",
        file_name="hybrid.pdf",
        file_path="uploads/hybrid.pdf",
        file_type="pdf",
        file_size=2048,
        status="current"
    )
    db.add(ver)
    db.flush()

    c1 = DocumentChunk(chunk_id="CHK-1", document_version_id="VER-HYB-01", chunk_index=0, content="Confidentiality and non-disclosure obligations shall persist for five years.")
    c2 = DocumentChunk(chunk_id="CHK-2", document_version_id="VER-HYB-01", chunk_index=1, content="Immediate termination is allowed upon regulatory statutory non-compliance.")
    c3 = DocumentChunk(chunk_id="CHK-3", document_version_id="VER-HYB-01", chunk_index=2, content="Arbitration in New York shall resolve all disputes arising under this agreement.")
    
    db.add_all([c1, c2, c3])
    db.commit()

    # Index in both stores
    sem_service.rebuild_index(db)
    kw_service.rebuild_index(db)

    hybrid_service = HybridSearchService(semantic_service=sem_service, keyword_service=kw_service)
    return hybrid_service

def test_hybrid_search_fusion(db, hybrid_components):
    hybrid_service = hybrid_components
    
    # Run hybrid search
    results = hybrid_service.search(db, "regulatory statutory non-compliance", top_k=2, mode=SearchMode.hybrid)
    assert len(results) > 0
    assert results[0]["chunk_id"] == "CHK-2"
    assert results[0]["retrieval_type"] in ["hybrid", "keyword", "semantic"]
    assert "score" in results[0]

def test_hybrid_search_modes(db, hybrid_components):
    hybrid_service = hybrid_components

    # Semantic mode
    sem_res = hybrid_service.search(db, "confidentiality five years", top_k=2, mode=SearchMode.semantic)
    assert len(sem_res) > 0
    assert sem_res[0]["retrieval_type"] == "semantic"

    # Keyword mode
    kw_res = hybrid_service.search(db, "arbitration New York", top_k=2, mode=SearchMode.keyword)
    assert len(kw_res) > 0
    assert kw_res[0]["retrieval_type"] == "keyword"

def test_empty_query_and_index(db, hybrid_components):
    hybrid_service = hybrid_components
    empty_res = hybrid_service.search(db, "", top_k=5)
    assert len(empty_res) == 0
