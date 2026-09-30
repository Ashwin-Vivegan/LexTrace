import pytest
from app.services.keyword_search import KeywordSearchService
from app.db.models import DocumentChunk, DocumentVersion, Document

@pytest.fixture
def fts_service():
    return KeywordSearchService()

def test_fts_init_and_sanitize(db, fts_service):
    fts_service.init_fts_table(db)
    status = fts_service.get_status(db)
    assert status["fts5_ready"] is True

    # Test sanitization
    sanitized = fts_service.sanitize_query('termination "due to" AND (regulatory: changes*)')
    assert "termination" in sanitized
    assert "regulatory" in sanitized
    assert ":" not in sanitized
    assert "(" not in sanitized

def test_fts_index_and_search(db, fts_service):
    # Setup test document and version
    doc = Document(document_id="DOC-FTS-01", document_name="FTS Test Agreement", document_type="contract")
    db.add(doc)
    db.flush()

    ver = DocumentVersion(
        version_id="VER-FTS-01",
        document_id="DOC-FTS-01",
        version_number="1.0",
        file_name="fts.pdf",
        file_path="uploads/fts.pdf",
        file_type="pdf",
        file_size=1024,
        status="current"
    )
    db.add(ver)
    db.flush()

    chunk1 = DocumentChunk(
        chunk_id="CHUNK-FTS-1",
        document_version_id="VER-FTS-01",
        chunk_index=0,
        content="The party may terminate this agreement due to regulatory compliance changes.",
        section_name="Termination"
    )
    chunk2 = DocumentChunk(
        chunk_id="CHUNK-FTS-2",
        document_version_id="VER-FTS-01",
        chunk_index=1,
        content="Indemnification shall cover third-party claims and liabilities.",
        section_name="Indemnity"
    )
    db.add(chunk1)
    db.add(chunk2)
    db.commit()

    # Index chunks in FTS5
    indexed_count = fts_service.index_chunks(db, [chunk1, chunk2])
    assert indexed_count == 2

    # Search FTS5
    results = fts_service.search(db, "regulatory compliance", top_k=5)
    assert len(results) >= 1
    assert results[0]["chunk_id"] == "CHUNK-FTS-1"
    assert results[0]["retrieval_type"] == "keyword"
    assert results[0]["score"] > 0

def test_fts_delete_and_rebuild(db, fts_service):
    doc = Document(document_id="DOC-FTS-02", document_name="Rebuild Test", document_type="contract")
    db.add(doc)
    db.flush()

    ver = DocumentVersion(
        version_id="VER-FTS-02",
        document_id="DOC-FTS-02",
        version_number="1.0",
        file_name="rebuild.pdf",
        file_path="uploads/rebuild.pdf",
        file_type="pdf",
        file_size=512,
        status="current"
    )
    db.add(ver)
    db.flush()

    chunk = DocumentChunk(
        chunk_id="CHUNK-REBUILD-1",
        document_version_id="VER-FTS-02",
        chunk_index=0,
        content="Statutory regulatory compliance requirements for legal entities.",
        section_name="Compliance"
    )
    db.add(chunk)
    db.commit()

    # Index chunk
    fts_service.index_chunks(db, [chunk])

    # Delete single chunk from FTS5
    fts_service.delete_chunk(db, "CHUNK-REBUILD-1")
    results = fts_service.search(db, "regulatory compliance", top_k=5)
    assert len(results) == 0

    # Rebuild index from SQLite document_chunks table
    count = fts_service.rebuild_index(db)
    assert count >= 1

    # Search again after rebuild
    results_after = fts_service.search(db, "regulatory compliance", top_k=5)
    assert len(results_after) == 1
    assert results_after[0]["chunk_id"] == "CHUNK-REBUILD-1"
