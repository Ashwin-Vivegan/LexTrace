import os
import pytest
from app.services.vector_store.faiss_store import FaissVectorStore
import tempfile

@pytest.fixture
def temp_persist_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d

def test_faiss_store_add_and_search(temp_persist_dir):
    store = FaissVectorStore(persist_dir=temp_persist_dir, dimension=3)
    assert store.count == 0
    
    # Vectors must be L2 normalized for IndexFlatIP
    # Note: these test vectors are manually normalized to length 1
    # [1, 0, 0] length = 1
    # [0, 1, 0] length = 1
    
    chunk_ids = ["chunk1", "chunk2"]
    vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    
    store.add_vectors(chunk_ids, vectors)
    assert store.count == 2
    
    # Search for [1,0,0] - chunk1 should be exact match (score 1.0)
    results = store.search([1.0, 0.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0][0] == "chunk1"
    assert results[0][1] == pytest.approx(1.0, 0.001)

def test_faiss_store_persistence(temp_persist_dir):
    # Create and add
    store1 = FaissVectorStore(persist_dir=temp_persist_dir, dimension=3)
    chunk_ids = ["c1"]
    vectors = [[0.0, 0.0, 1.0]]
    store1.add_vectors(chunk_ids, vectors)
    store1.save()
    
    assert os.path.exists(os.path.join(temp_persist_dir, "lextrace.index"))
    assert os.path.exists(os.path.join(temp_persist_dir, "chunk_mapping.json"))
    assert os.path.exists(os.path.join(temp_persist_dir, "metadata.json"))
    
    # Load in new instance
    store2 = FaissVectorStore(persist_dir=temp_persist_dir, dimension=3)
    assert store2.count == 1
    results = store2.search([0.0, 0.0, 1.0], top_k=1)
    assert results[0][0] == "c1"

def test_faiss_store_duplicate_prevention(temp_persist_dir):
    store = FaissVectorStore(persist_dir=temp_persist_dir, dimension=3)
    
    store.add_vectors(["dup"], [[1.0, 0.0, 0.0]])
    assert store.count == 1
    
    # Adding same chunk_id again should be ignored
    store.add_vectors(["dup"], [[0.0, 1.0, 0.0]])
    assert store.count == 1
