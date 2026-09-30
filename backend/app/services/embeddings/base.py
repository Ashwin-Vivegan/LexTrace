from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """
    Base interface for an embedding provider.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single string into a vector."""
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of strings into a list of vectors."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of the embedding vectors produced."""
        pass
