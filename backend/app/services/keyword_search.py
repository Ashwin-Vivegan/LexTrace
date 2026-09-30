import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models import DocumentChunk, DocumentVersion, Document

logger = logging.getLogger(__name__)

class KeywordSearchService:
    """
    SQLite FTS5 full-text keyword retrieval service.
    Indexes DocumentChunk content in an FTS5 virtual table (`document_chunks_fts`)
    and retrieves chunks based on BM25 relevance scoring.
    """
    def __init__(self):
        pass

    def init_fts_table(self, db: Session) -> None:
        """
        Ensures that the FTS5 virtual table exists in SQLite.
        """
        create_sql = text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts USING fts5(
                chunk_id UNINDEXED,
                content,
                tokenize='unicode61'
            );
        """)
        try:
            db.execute(create_sql)
            db.commit()
            logger.info("FTS5 table 'document_chunks_fts' initialized successfully.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error initializing FTS5 virtual table: {e}")
            raise e

    def sanitize_query(self, query: str) -> str:
        """
        Sanitizes user input query for FTS5 syntax safety.
        Strips special FTS5 operators that cause syntax errors and formats as space-separated tokens.
        """
        if not query:
            return ""
        # Remove characters that cause FTS5 syntax errors (quotes, colons, parens, asterisks, etc.)
        cleaned = re.sub(r'[^\w\s]', ' ', query)
        words = [w.strip() for w in cleaned.split() if w.strip()]
        if not words:
            return ""
        # Join words to perform match
        return " OR ".join(f'"{w}"' for w in words)

    def index_chunk(self, db: Session, chunk_id: str, content: str) -> None:
        """
        Inserts or updates a single DocumentChunk record in the FTS5 virtual table.
        """
        self.init_fts_table(db)
        delete_sql = text("DELETE FROM document_chunks_fts WHERE chunk_id = :chunk_id")
        insert_sql = text("INSERT INTO document_chunks_fts (chunk_id, content) VALUES (:chunk_id, :content)")
        try:
            db.execute(delete_sql, {"chunk_id": chunk_id})
            db.execute(insert_sql, {"chunk_id": chunk_id, "content": content})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to index chunk {chunk_id} in FTS5: {e}")

    def index_chunks(self, db: Session, chunks: List[DocumentChunk]) -> int:
        """
        Inserts or updates a list of DocumentChunk records in the FTS5 virtual table.
        """
        if not chunks:
            return 0
        self.init_fts_table(db)
        try:
            delete_sql = text("DELETE FROM document_chunks_fts WHERE chunk_id = :chunk_id")
            insert_sql = text("INSERT INTO document_chunks_fts (chunk_id, content) VALUES (:chunk_id, :content)")
            for c in chunks:
                db.execute(delete_sql, {"chunk_id": c.chunk_id})
                db.execute(insert_sql, {"chunk_id": c.chunk_id, "content": c.content})
            db.commit()
            return len(chunks)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to batch index chunks in FTS5: {e}")
            return 0

    def delete_chunk(self, db: Session, chunk_id: str) -> None:
        """
        Deletes a single chunk from the FTS5 virtual table.
        """
        self.init_fts_table(db)
        try:
            db.execute(text("DELETE FROM document_chunks_fts WHERE chunk_id = :chunk_id"), {"chunk_id": chunk_id})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete chunk {chunk_id} from FTS5: {e}")

    def delete_version_chunks(self, db: Session, version_id: str) -> None:
        """
        Deletes all chunks belonging to a document version from FTS5.
        """
        self.init_fts_table(db)
        try:
            chunk_ids = [
                row[0] for row in db.query(DocumentChunk.chunk_id).filter(DocumentChunk.document_version_id == version_id).all()
            ]
            delete_sql = text("DELETE FROM document_chunks_fts WHERE chunk_id = :chunk_id")
            for cid in chunk_ids:
                db.execute(delete_sql, {"chunk_id": cid})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete version chunks for {version_id} from FTS5: {e}")

    def rebuild_index(self, db: Session) -> int:
        """
        Clears and rebuilds the FTS5 virtual table from all active DocumentChunk records in SQLite.
        """
        self.init_fts_table(db)
        try:
            db.execute(text("DELETE FROM document_chunks_fts"))
            rebuild_sql = text("""
                INSERT INTO document_chunks_fts (chunk_id, content)
                SELECT chunk_id, content FROM document_chunks;
            """)
            db.execute(rebuild_sql)
            db.commit()
            
            # Count indexed
            count = db.execute(text("SELECT count(*) FROM document_chunks_fts")).scalar()
            logger.info(f"FTS5 index rebuilt successfully with {count} chunks.")
            return count or 0
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to rebuild FTS5 index: {e}")
            raise e

    def get_status(self, db: Session) -> Dict[str, Any]:
        """
        Returns FTS5 index count and status.
        """
        self.init_fts_table(db)
        try:
            count = db.execute(text("SELECT count(*) FROM document_chunks_fts")).scalar() or 0
            return {
                "fts5_count": count,
                "fts5_ready": True
            }
        except Exception as e:
            logger.error(f"Error checking FTS5 index status: {e}")
            return {
                "fts5_count": 0,
                "fts5_ready": False
            }

    def search(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes an FTS5 MATCH search query over DocumentChunk content and returns BM25-ranked results with metadata.
        """
        if not query or not query.strip():
            return []

        self.init_fts_table(db)
        sanitized = self.sanitize_query(query)
        if not sanitized:
            return []

        try:
            fts_sql = text("""
                SELECT chunk_id, -bm25(document_chunks_fts) AS bm25_score
                FROM document_chunks_fts
                WHERE document_chunks_fts MATCH :query
                ORDER BY bm25_score DESC
                LIMIT :top_k
            """)
            rows = db.execute(fts_sql, {"query": sanitized, "top_k": top_k}).fetchall()

            if not rows:
                return []

            chunk_ids = [row[0] for row in rows]
            score_map = {row[0]: float(row[1]) for row in rows}

            chunks = db.query(DocumentChunk, DocumentVersion, Document).join(
                DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.version_id
            ).join(
                Document, DocumentVersion.document_id == Document.document_id
            ).filter(
                DocumentChunk.chunk_id.in_(chunk_ids)
            ).all()

            results = []
            for chunk, version, doc in chunks:
                raw_score = score_map.get(chunk.chunk_id, 0.0)
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "score": raw_score,
                    "retrieval_type": "keyword",
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

            results.sort(key=lambda x: x["score"], reverse=True)
            return results

        except Exception as e:
            logger.error(f"Keyword search failed for query '{query}': {e}")
            return []
