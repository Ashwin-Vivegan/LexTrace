import os
import json
import logging
from typing import List, Tuple
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

from app.services.vector_store.base import VectorStore

logger = logging.getLogger(__name__)

class FaissVectorStore(VectorStore):
    """
    Vector store implementation using FAISS IndexFlatIP.
    Since IndexFlatIP expects L2 normalized vectors for Cosine Similarity,
    we assume the vectors passed in are already normalized.
    """
    
    def __init__(self, persist_dir: str, dimension: int):
        if faiss is None:
            raise ImportError("faiss-cpu is not installed.")
            
        self.persist_dir = persist_dir
        self.dimension = dimension
        
        self.index_path = os.path.join(self.persist_dir, "lextrace.index")
        self.mapping_path = os.path.join(self.persist_dir, "chunk_mapping.json")
        self.metadata_path = os.path.join(self.persist_dir, "metadata.json")
        
        # In FAISS, IndexFlatIP computes the inner product. 
        # If vectors are L2-normalized, inner product equals cosine similarity.
        self.index = faiss.IndexFlatIP(dimension)
        
        # FAISS uses integer IDs. We need to map FAISS IDs (0 to N-1) to our string chunk_ids.
        # list of chunk_ids where the index in the list matches the FAISS integer ID.
        self.chunk_id_mapping: List[str] = []
        
        self.load()

    def add_vectors(self, chunk_ids: List[str], vectors: List[List[float]]) -> None:
        if not chunk_ids or not vectors:
            return
            
        if len(chunk_ids) != len(vectors):
            raise ValueError("Number of chunk_ids must match number of vectors.")
            
        # Check if chunks already exist in mapping to avoid exact duplicates
        # A robust system would delete old vectors, but FAISS IndexFlat doesn't support deletion easily.
        # For simplicity and given the requirements, we'll only add if they don't exist.
        # If they exist, we just skip (or ideally, we rebuild index if doing a full reindex).
        
        existing_set = set(self.chunk_id_mapping)
        new_chunk_ids = []
        new_vectors = []
        
        for cid, vec in zip(chunk_ids, vectors):
            if cid not in existing_set:
                new_chunk_ids.append(cid)
                new_vectors.append(vec)
                
        if not new_chunk_ids:
            return
            
        vectors_np = np.array(new_vectors, dtype=np.float32)
        
        # Add to FAISS
        self.index.add(vectors_np)
        
        # Update mapping
        self.chunk_id_mapping.extend(new_chunk_ids)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        if self.count == 0:
            return []
            
        query_np = np.array([query_vector], dtype=np.float32)
        
        # FAISS search returns distances (similarities for IP) and indices
        similarities, indices = self.index.search(query_np, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunk_id_mapping):
                chunk_id = self.chunk_id_mapping[idx]
                score = float(similarities[0][i])
                results.append((chunk_id, score))
                
        return results

    def clear(self) -> None:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunk_id_mapping = []

    def save(self) -> None:
        os.makedirs(self.persist_dir, exist_ok=True)
        
        faiss.write_index(self.index, self.index_path)
        
        with open(self.mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunk_id_mapping, f)
            
        metadata = {
            "dimension": self.dimension,
            "vector_count": self.count,
        }
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
            
        logger.info(f"Saved FAISS index with {self.count} vectors to {self.persist_dir}")

    def load(self) -> None:
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.mapping_path, 'r', encoding='utf-8') as f:
                    self.chunk_id_mapping = json.load(f)
                logger.info(f"Loaded FAISS index with {self.count} vectors from {self.persist_dir}")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                self.clear()
        else:
            self.clear()

    @property
    def count(self) -> int:
        return self.index.ntotal
