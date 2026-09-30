import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk, DocumentVersion, Document
from app.services.embeddings.base import EmbeddingProvider
from app.services.vector_store.base import VectorStore

logger = logging.getLogger(__name__)

class SemanticSearchService:
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_document_version(self, db: Session, version_id: str, batch_size: int = 100) -> int:
        """
        Extract chunks for a given version from SQLite, embed them, and add them to the vector store.
        Returns the number of chunks indexed.
        """
        logger.info(f"Indexing document version: {version_id}")
        
        # Get all chunks for this version
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_version_id == version_id).order_by(DocumentChunk.chunk_index).all()
        
        if not chunks:
            logger.warning(f"No chunks found for version {version_id}")
            return 0
            
        indexed_count = 0
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts_to_embed = [chunk.content for chunk in batch]
            chunk_ids = [chunk.chunk_id for chunk in batch]
            
            try:
                logger.info(f"Embedding batch of {len(batch)} chunks...")
                vectors = self.embedding_provider.embed_texts(texts_to_embed)
                
                logger.info(f"Adding batch of {len(batch)} vectors to FAISS...")
                self.vector_store.add_vectors(chunk_ids, vectors)
                
                indexed_count += len(batch)
            except Exception as e:
                logger.error(f"Failed to embed and index batch: {e}")
                # For robustness, we might want to continue or abort. Let's raise to caller.
                raise e
                
        # Save after modifying
        self.vector_store.save()
        logger.info(f"Successfully indexed {indexed_count} chunks for version {version_id}")
        return indexed_count

    def rebuild_index(self, db: Session, batch_size: int = 200) -> int:
        """
        Clear the existing index and re-index all current document chunks from SQLite.
        """
        logger.info("Starting full index rebuild...")
        self.vector_store.clear()
        
        # Get all chunks
        total_indexed = 0
        offset = 0
        
        while True:
            chunks = db.query(DocumentChunk).order_by(DocumentChunk.id).offset(offset).limit(batch_size).all()
            if not chunks:
                break
                
            texts_to_embed = [chunk.content for chunk in chunks]
            chunk_ids = [chunk.chunk_id for chunk in chunks]
            
            vectors = self.embedding_provider.embed_texts(texts_to_embed)
            self.vector_store.add_vectors(chunk_ids, vectors)
            
            total_indexed += len(chunks)
            offset += batch_size
            logger.info(f"Indexed {total_indexed} chunks so far...")
            
        self.vector_store.save()
        logger.info(f"Full index rebuild complete. Total vectors: {total_indexed}")
        return total_indexed

    def search(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search for a query and return enriched metadata from SQLite.
        """
        if not query.strip():
            return []
            
        if self.vector_store.count == 0:
            logger.warning("Search called on an empty vector store.")
            return []
            
        # Embed the query
        query_vector = self.embedding_provider.embed_text(query)
        
        # Search the vector store
        search_results = self.vector_store.search(query_vector, top_k=top_k)
        
        if not search_results:
            return []
            
        # Extract chunk_ids and scores
        chunk_ids = [res[0] for res in search_results]
        score_map = {res[0]: res[1] for res in search_results}
        
        # Fetch metadata from SQLite
        # We need chunk, version, and document info
        chunks = db.query(DocumentChunk, DocumentVersion, Document).join(
            DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.version_id
        ).join(
            Document, DocumentVersion.document_id == Document.document_id
        ).filter(
            DocumentChunk.chunk_id.in_(chunk_ids)
        ).all()
        
        # Build the enriched results
        results = []
        for chunk, version, doc in chunks:
            # We want to maintain order by score if possible, but SQLAlchemy in_() doesn't preserve order.
            # We'll map and sort them manually.
            pass # sorting later
            
            results.append({
                "chunk_id": chunk.chunk_id,
                "similarity_score": score_map.get(chunk.chunk_id, 0.0),
                "document_id": doc.document_id,
                "document_name": doc.document_name,
                "document_type": doc.document_type,
                "jurisdiction": doc.jurisdiction,
                "practice_area": doc.practice_area,
                "version_id": version.version_id,
                "version_number": version.version_number,
                "section_name": chunk.section_name,
                "subsection_name": chunk.subsection_name,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content
            })
            
        # Sort by similarity_score descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results

    def get_status(self) -> Dict[str, Any]:
        """
        Return the status of the semantic search index.
        """
        return {
            "vector_count": self.vector_store.count,
            "dimension": self.embedding_provider.dimension,
            "is_ready": self.vector_store.count > 0
        }
