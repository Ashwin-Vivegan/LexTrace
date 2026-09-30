import os
import sys
import logging
import time

# Ensure UTF-8 output formatting for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Document, DocumentVersion, DocumentChunk
from app.services.embeddings.local import LocalSentenceTransformerProvider
from app.services.vector_store.faiss_store import FaissVectorStore
from app.services.semantic_search import SemanticSearchService
from app.services.keyword_search import KeywordSearchService
from app.services.hybrid_search import HybridSearchService
from app.services.rag_service import RAGService, INSUFFICIENT_EVIDENCE_TEXT
from app.services.llm_provider import GroqLLMProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluate_rag")

def setup_rag_benchmark_data(db: Session):
    """Populates synthetic legal benchmark data if empty."""
    if db.query(Document).filter(Document.document_id == "DOC-RAG-001").count() == 0:
        logger.info("Populating synthetic benchmark data for RAG evaluation...")
        doc1 = Document(
            document_id="DOC-RAG-001",
            document_name="Executive Employment Agreement 2026",
            document_type="contract",
            jurisdiction="Delaware",
            practice_area="Employment"
        )
        doc2 = Document(
            document_id="DOC-RAG-002",
            document_name="Corporate Information Security Policy",
            document_type="policy",
            jurisdiction="Federal",
            practice_area="Compliance"
        )
        db.add_all([doc1, doc2])
        db.flush()

        v1 = DocumentVersion(
            version_id="VER-RAG-001-V2_0",
            document_id="DOC-RAG-001",
            version_number="2.0",
            file_name="exec_emp_v2.pdf",
            file_path="uploads/exec_emp_v2.pdf",
            file_type="pdf",
            file_size=15360,
            status="current"
        )
        v2 = DocumentVersion(
            version_id="VER-RAG-002-V1_0",
            document_id="DOC-RAG-002",
            version_number="1.0",
            file_name="security_policy.pdf",
            file_path="uploads/security_policy.pdf",
            file_type="pdf",
            file_size=12288,
            status="current"
        )
        db.add_all([v1, v2])
        db.flush()

        chunks = [
            DocumentChunk(
                chunk_id="CHK-EMP-01",
                document_version_id="VER-RAG-001-V2_0",
                chunk_index=0,
                content="Section 7.1 Termination by Company Without Cause. The Company may terminate Executive's employment at any time without Cause upon providing thirty (30) days prior written notice to Executive.",
                section_name="Termination",
                page_number=7
            ),
            DocumentChunk(
                chunk_id="CHK-EMP-02",
                document_version_id="VER-RAG-001-V2_0",
                chunk_index=1,
                content="Section 7.2 Severance Pay. Upon termination without Cause, Executive shall receive six (6) months of base salary continuation as severance pay.",
                section_name="Termination",
                page_number=8
            ),
            DocumentChunk(
                chunk_id="CHK-SEC-01",
                document_version_id="VER-RAG-002-V1_0",
                chunk_index=0,
                content="Section 4.3 Data Encryption Standard. All confidential employee and client data stored at rest must be encrypted using AES-256 encryption algorithm.",
                section_name="Data Protection",
                page_number=12
            )
        ]
        db.add_all(chunks)
        db.commit()

        # Index in FAISS & FTS5
        sem_service = SemanticSearchService(
            embedding_provider=LocalSentenceTransformerProvider(),
            vector_store=FaissVectorStore(persist_dir=os.path.join(os.path.dirname(__file__), "..", "data", "vector_store"), dimension=384)
        )
        kw_service = KeywordSearchService()
        sem_service.rebuild_index(db)
        kw_service.rebuild_index(db)
        logger.info("RAG Benchmark data populated and indexed.")

def run_rag_evaluation():
    db = SessionLocal()
    setup_rag_benchmark_data(db)

    # Instantiate search & RAG pipeline
    persist_dir = os.path.join(os.path.dirname(__file__), "..", "data", "vector_store")
    embed_provider = LocalSentenceTransformerProvider()
    vector_store = FaissVectorStore(persist_dir=persist_dir, dimension=embed_provider.dimension)

    sem_service = SemanticSearchService(embedding_provider=embed_provider, vector_store=vector_store)
    kw_service = KeywordSearchService()
    hybrid_service = HybridSearchService(semantic_service=sem_service, keyword_service=kw_service)
    
    groq_provider = GroqLLMProvider()
    rag_service = RAGService(hybrid_search_service=hybrid_service, llm_provider=groq_provider)

    print("\n==================================================")
    print("LEXTRACE MILESTONE 5 — RAG EVALUATION BENCHMARK")
    print("==================================================")

    # SCENARIO 1: Direct Question
    print("\n--- SCENARIO 1: DIRECT QUESTION ---")
    q1 = "What is the written notice requirement for termination without Cause?"
    print(f"Question: '{q1}'")
    r1 = rag_service.ask(db, q1, top_k=3)
    print(f"Answer:\n{r1['answer']}")
    print(f"Citations ({len(r1['citations'])}): {[c['chunk_id'] + ' (' + c['document_name'] + ')' for c in r1['citations']]}")
    assert r1['answer'] != INSUFFICIENT_EVIDENCE_TEXT
    assert len(r1['citations']) > 0

    # SCENARIO 2: Multi-Source Question
    print("\n--- SCENARIO 2: MULTI-SOURCE QUESTION ---")
    q2 = "What notice and severance pay apply to executive termination, and what is the data encryption standard?"
    print(f"Question: '{q2}'")
    r2 = rag_service.ask(db, q2, top_k=5)
    print(f"Answer:\n{r2['answer']}")
    print(f"Citations ({len(r2['citations'])}): {[c['chunk_id'] + ' (' + c['document_name'] + ')' for c in r2['citations']]}")
    assert r2['answer'] != INSUFFICIENT_EVIDENCE_TEXT
    assert len(r2['citations']) >= 2

    # SCENARIO 3: Unknown / Unsupported Question
    print("\n--- SCENARIO 3: UNKNOWN QUESTION (REFUSAL) ---")
    q3 = "What is the company policy regarding nuclear submarine space propulsion systems?"
    print(f"Question: '{q3}'")
    r3 = rag_service.ask(db, q3, top_k=3)
    print(f"Answer:\n{r3['answer']}")
    print(f"Citations ({len(r3['citations'])}): {r3['citations']}")
    assert r3['answer'] == INSUFFICIENT_EVIDENCE_TEXT
    assert len(r3['citations']) == 0

    print("\n==================================================")
    print("ALL 3 MANDATORY DEMO SCENARIOS PASSED VERIFICATION!")
    print("==================================================\n")

if __name__ == "__main__":
    run_rag_evaluation()
