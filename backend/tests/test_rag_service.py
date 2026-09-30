import pytest
from unittest.mock import MagicMock
from app.services.rag_service import RAGService, INSUFFICIENT_EVIDENCE_TEXT
from app.services.llm_provider import LLMProvider
from app.db.models import Document, DocumentVersion, DocumentChunk

class MockLLMProvider(LLMProvider):
    def __init__(self, response_text="The agreement allows termination with 30 days notice."):
        self.response_text = response_text
        self.model = "Mock-LLM-70B"

    def generate_answer(self, prompt: str, system_prompt: str) -> str:
        return self.response_text

def test_rag_service_empty_query(db):
    mock_hybrid = MagicMock()
    rag_service = RAGService(hybrid_search_service=mock_hybrid, llm_provider=MockLLMProvider())
    
    with pytest.raises(ValueError, match="empty or whitespace-only"):
        rag_service.ask(db, query="   ")

def test_rag_service_zero_evidence(db):
    mock_hybrid = MagicMock()
    mock_hybrid.search.return_value = []
    rag_service = RAGService(hybrid_search_service=mock_hybrid, llm_provider=MockLLMProvider())

    res = rag_service.ask(db, query="What is the nuclear submarine policy?")
    assert res["answer"] == INSUFFICIENT_EVIDENCE_TEXT
    assert len(res["citations"]) == 0
    assert res["metadata"]["chunks_retrieved"] == 0

def test_rag_service_successful_grounded_answer(db):
    # Setup test DB entities
    doc = Document(document_id="DOC-RAG-TEST", document_name="RAG Service Test Doc", document_type="contract")
    db.add(doc)
    db.flush()

    ver = DocumentVersion(
        version_id="VER-RAG-TEST",
        document_id="DOC-RAG-TEST",
        version_number="1.0",
        file_name="test.pdf",
        file_path="uploads/test.pdf",
        file_type="pdf",
        file_size=1024,
        status="current"
    )
    db.add(ver)
    db.flush()

    chunk = DocumentChunk(
        chunk_id="CHK-RAG-1",
        document_version_id="VER-RAG-TEST",
        chunk_index=0,
        content="Either party may terminate this agreement with 30 days written notice.",
        section_name="Termination",
        page_number=4
    )
    db.add(chunk)
    db.commit()

    # Mock hybrid search returning enriched dict
    mock_hybrid = MagicMock()
    mock_hybrid.search.return_value = [{
        "chunk_id": "CHK-RAG-1",
        "document_id": "DOC-RAG-TEST",
        "document_name": "RAG Service Test Doc",
        "document_type": "contract",
        "jurisdiction": "Delaware",
        "practice_area": "Corporate",
        "version_id": "VER-RAG-TEST",
        "version_number": "1.0",
        "section_name": "Termination",
        "subsection_name": None,
        "page_number": 4,
        "chunk_index": 0,
        "content": "Either party may terminate this agreement with 30 days written notice.",
        "score": 0.95,
        "retrieval_type": "hybrid"
    }]

    mock_llm = MockLLMProvider("Either party can terminate with 30 days notice.")
    rag_service = RAGService(hybrid_search_service=mock_hybrid, llm_provider=mock_llm)

    res = rag_service.ask(db, query="What are the termination rules?")
    assert "terminate with 30 days notice" in res["answer"]
    assert len(res["citations"]) == 1
    assert res["citations"][0]["chunk_id"] == "CHK-RAG-1"
    assert res["citations"][0]["document_name"] == "RAG Service Test Doc"
    assert res["citations"][0]["version_number"] == "1.0"
    assert res["citations"][0]["section_name"] == "Termination"

def test_rag_service_llm_failure_fallback(db):
    mock_hybrid = MagicMock()
    mock_hybrid.search.return_value = [{"chunk_id": "C1", "document_id": "D1", "document_name": "Doc", "document_type": "contract", "version_id": "V1", "version_number": "1.0", "chunk_index": 0, "content": "Text"}]
    
    failing_llm = MagicMock()
    failing_llm.generate_answer.side_effect = RuntimeError("API Error")

    rag_service = RAGService(hybrid_search_service=mock_hybrid, llm_provider=failing_llm)
    res = rag_service.ask(db, query="Test query")
    assert res["answer"] == INSUFFICIENT_EVIDENCE_TEXT
    assert len(res["citations"]) == 0
