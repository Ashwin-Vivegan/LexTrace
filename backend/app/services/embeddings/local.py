from typing import List
import logging
from app.services.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

class LocalSentenceTransformerProvider(EmbeddingProvider):
    """
    Embedding provider using local SentenceTransformers model.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None
        self._dimension = 384  # Default for all-MiniLM-L6-v2, updated on load

    def _load_model(self):
        if self._model is None:
            logger.info(f"Loading local embedding model: {self._model_name}")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
                # get_sentence_embedding_dimension is deprecated; use get_embedding_dimension if available
                if hasattr(self._model, 'get_embedding_dimension'):
                    self._dimension = self._model.get_embedding_dimension()
                else:
                    self._dimension = self._model.get_sentence_embedding_dimension()
                logger.info(f"Model loaded. Dimension: {self._dimension}")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is not installed. "
                    "Please install it using 'pip install sentence-transformers'"
                )

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        # encode returns a numpy array, convert to list of floats
        vector = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._load_model()
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._dimension
