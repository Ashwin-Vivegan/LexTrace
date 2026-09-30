from abc import ABC, abstractmethod
from typing import List, Tuple

class VectorStore(ABC):
    """
    Base interface for a vector store.
    """

    @abstractmethod
    def add_vectors(self, chunk_ids: List[str], vectors: List[List[float]]) -> None:
        """
        Add a list of vectors mapping to the given chunk_ids.
        If a chunk_id already exists, its vector should ideally be updated or duplicated handled.
        For simplicity, some implementations might just drop and recreate or append.
        """
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for the top_k most similar vectors.
        Returns a list of tuples: (chunk_id, similarity_score)
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire index and mappings."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Persist the index and mappings to disk."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Load the index and mappings from disk."""
        pass
    
    @property
    @abstractmethod
    def count(self) -> int:
        """Return the number of vectors in the store."""
        pass
