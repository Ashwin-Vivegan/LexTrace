import os
import sys
import logging

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db, engine, SessionLocal
from app.db.models import Document, DocumentVersion, DocumentChunk
from app.services.embeddings.local import LocalSentenceTransformerProvider
from app.services.vector_store.faiss_store import FaissVectorStore
from app.services.semantic_search import SemanticSearchService
from app.services.keyword_search import KeywordSearchService
from app.services.hybrid_search import HybridSearchService
from app.schemas.search import SearchMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluate_search")

def setup_eval_data(db):
    """
    Populates synthetic legal benchmark data if database is empty.
    """
    if db.query(Document).count() == 0:
        logger.info("Populating synthetic benchmark legal document chunks...")
        doc = Document(
            document_id="DOC-EVAL-001",
            document_name="Master Services Agreement 2026",
            document_type="contract",
            jurisdiction="Delaware",
            practice_area="Corporate"
        )
        db.add(doc)
        db.flush()

        ver = DocumentVersion(
            version_id="DOC-EVAL-001-V1_0",
            document_id="DOC-EVAL-001",
            version_number="1.0",
            file_name="msa_2026.pdf",
            file_path="uploads/DOC-EVAL-001/v1_0/msa_2026.pdf",
            file_type="pdf",
            file_size=20480,
            extracted_text="Sample text",
            status="current"
        )
        db.add(ver)
        db.flush()

        eval_chunks = [
            ("CHUNK-001", "Section 14.2 Termination Due to Regulatory Changes. Either party may terminate this Agreement immediately upon written notice if any regulatory body introduces rules prohibiting the services.", "Termination", "Regulatory Termination", 1),
            ("CHUNK-002", "Section 8.1 Data Protection and GDPR Compliance. The Service Provider shall implement appropriate technical and organizational measures to safeguard personal data.", "Data Protection", "GDPR Compliance", 2),
            ("CHUNK-003", "Section 19.4 Governing Law and Jurisdiction. This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.", "Governing Law", "Jurisdiction", 3),
            ("CHUNK-004", "Section 12.3 Indemnification Obligations. Each party agrees to defend, indemnify, and hold harmless the other party against any third-party claims arising from breach.", "Indemnification", "Third-Party Claims", 4),
            ("CHUNK-005", "Section 5.2 Limitation of Liability. Neither party's aggregate liability under this Agreement shall exceed the total fees paid in the twelve months preceding the event.", "Liability", "Aggregate Cap", 5)
        ]

        for cid, content, sec, subsec, pnum in eval_chunks:
            chunk = DocumentChunk(
                chunk_id=cid,
                document_version_id="DOC-EVAL-001-V1_0",
                chunk_index=pnum - 1,
                content=content,
                section_name=sec,
                subsection_name=subsec,
                page_number=pnum
            )
            db.add(chunk)

        db.commit()
        logger.info("Synthetic benchmark dataset populated.")

def run_evaluation():
    db = SessionLocal()
    setup_eval_data(db)

    # Initialize services
    persist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vector_store")
    embed_provider = LocalSentenceTransformerProvider()
    vector_store = FaissVectorStore(persist_dir=persist_dir, dimension=embed_provider.dimension)
    
    sem_service = SemanticSearchService(embedding_provider=embed_provider, vector_store=vector_store)
    kw_service = KeywordSearchService()
    hybrid_service = HybridSearchService(semantic_service=sem_service, keyword_service=kw_service)

    # Rebuild indices
    logger.info("Rebuilding FAISS and FTS5 indices for evaluation...")
    sem_service.rebuild_index(db)
    kw_service.rebuild_index(db)

    # Benchmark test queries with target chunk IDs
    eval_queries = [
        {
            "query": "termination due to regulatory changes and new rules",
            "target_chunk_id": "CHUNK-001"
        },
        {
            "query": "data protection GDPR technical measures",
            "target_chunk_id": "CHUNK-002"
        },
        {
            "query": "governing law State of Delaware jurisdiction",
            "target_chunk_id": "CHUNK-003"
        },
        {
            "query": "indemnification defend hold harmless third-party claims",
            "target_chunk_id": "CHUNK-004"
        },
        {
            "query": "limitation of liability aggregate cap twelve months",
            "target_chunk_id": "CHUNK-005"
        }
    ]

    modes = [SearchMode.semantic, SearchMode.keyword, SearchMode.hybrid]
    metrics = {m.value: {"hit@1": 0, "hit@5": 0, "mrr": 0.0, "total": len(eval_queries)} for m in modes}

    for mode in modes:
        mode_key = mode.value
        for item in eval_queries:
            q = item["query"]
            target = item["target_chunk_id"]

            results = hybrid_service.search(db, q, top_k=5, mode=mode)
            retrieved_ids = [res["chunk_id"] for res in results]

            # Hit@1
            if retrieved_ids and retrieved_ids[0] == target:
                metrics[mode_key]["hit@1"] += 1

            # Hit@5 & MRR
            if target in retrieved_ids:
                metrics[mode_key]["hit@5"] += 1
                rank = retrieved_ids.index(target) + 1
                metrics[mode_key]["mrr"] += (1.0 / rank)

    print("\n==================================================")
    print("HYBRID RETRIEVAL BENCHMARK EVALUATION RESULTS")
    print("==================================================")
    for mode_key, data in metrics.items():
        total = data["total"]
        h1 = (data["hit@1"] / total) * 100
        h5 = (data["hit@5"] / total) * 100
        mrr = (data["mrr"] / total)
        print(f"Mode: {mode_key.upper():<10} | Hit@1: {h1:5.1f}% | Hit@5: {h5:5.1f}% | MRR: {mrr:.4f}")
    print("==================================================\n")

    return metrics

if __name__ == "__main__":
    run_evaluation()
