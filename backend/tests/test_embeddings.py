import pytest
from app.services.embeddings.local import LocalSentenceTransformerProvider
from app.services.embeddings.base import EmbeddingProvider

def test_local_provider_loads():
    provider = LocalSentenceTransformerProvider()
    assert isinstance(provider, EmbeddingProvider)
    # The dimension is checked on load
    assert provider.dimension == 384
    
def test_local_provider_embed_text():
    provider = LocalSentenceTransformerProvider()
    vector = provider.embed_text("Test query")
    assert isinstance(vector, list)
    assert len(vector) == 384
    assert isinstance(vector[0], float)

def test_local_provider_embed_texts():
    provider = LocalSentenceTransformerProvider()
    vectors = provider.embed_texts(["First text", "Second text"])
    assert isinstance(vectors, list)
    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384
