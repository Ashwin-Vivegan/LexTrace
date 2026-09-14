
import pytest
from app.services.document_chunker import DocumentChunker, parse_heading
from app.db.models import Document, DocumentVersion, DocumentChunk

def test_heading_parsing():
    """Test legal section and subsection heading regex detection."""
    sec1, sub1 = parse_heading("SECTION 4.1: CORPORATE GOVERNANCE AND VOTING RIGHTS")
    assert sec1 is not None
    assert sub1 is None

    sec2, sub2 = parse_heading("ARTICLE 14: HUMAN OVERSIGHT AND TRACE")
    assert sec2 is not None

    sec3, sub3 = parse_heading("(a) Right of First Refusal")
    assert sub3 is not None

def test_basic_text_chunking():
    """Test basic chunking algorithm on structured page blocks."""
    page_blocks = [
        {
            "page_number": 1,
            "text": "SECTION 1. DEFINITIONS\n\n'Agreement' means this Master Services Agreement.\n\n'Effective Date' means January 1, 2026."
        }
    ]

    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].section_name is not None
    assert "DEFINITIONS" in chunks[0].section_name
    assert chunks[0].page_number == 1

def test_paragraph_boundaries():
    """Test that paragraph boundaries are respected during chunking."""
    para1 = "Paragraph 1 detailing general provisions and corporate compliance rules."
    para2 = "Paragraph 2 detailing indemnification liabilities and warranties."
    page_blocks = [{"page_number": 1, "text": f"{para1}\n\n{para2}"}]

    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks, chunk_size=100, chunk_overlap=10)
    assert len(chunks) >= 2
    assert "Paragraph 1" in chunks[0].content

def test_chunk_overlap():
    """Test overlap retention between adjacent chunks."""
    block_text = "WordA WordB WordC WordD WordE WordF WordG WordH WordI WordJ WordK WordL WordM WordN WordO"
    page_blocks = [{"page_number": 1, "text": block_text}]

    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks, chunk_size=40, chunk_overlap=15)
    if len(chunks) > 1:
        tail_c1 = chunks[0].content[-10:]
        assert tail_c1 in chunks[1].content

def test_section_detection():
    """
    Test that active section metadata propagates to generated chunks.
    Uses a small chunk_size so each section body paragraph forces a new chunk.
    """
    # Each paragraph is ~60-70 chars; chunk_size=80 forces a split after each one
    text = (
        "SECTION 1: GOVERNING LAW\n\n"
        "This contract is governed by the laws of England and Wales.\n\n"
        "SECTION 2: DISPUTE RESOLUTION\n\n"
        "Any disputes shall be submitted to arbitration proceedings in London."
    )
    page_blocks = [{"page_number": 1, "text": text}]

    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks, chunk_size=80, chunk_overlap=10)
    # With chunk_size=80, each section body line exceeds the limit independently
    assert len(chunks) >= 2
    # First chunk should carry the SECTION 1 heading as active section
    assert chunks[0].section_name is not None
    assert "SECTION 1" in chunks[0].section_name
    # Last chunk should carry SECTION 2 heading as active section
    last_chunk = chunks[-1]
    assert last_chunk.section_name is not None
    assert "SECTION 2" in last_chunk.section_name

def test_chunk_ordering():
    """Test that chunk_index strictly preserves original sequential ordering 0..N."""
    paragraphs = [f"Section {i}: Paragraph text content block for testing sequence." for i in range(1, 10)]
    text = "\n\n".join(paragraphs)
    page_blocks = [{"page_number": 1, "text": text}]

    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks, chunk_size=150, chunk_overlap=20)
    for idx, c in enumerate(chunks):
        assert c.chunk_index == idx

def test_empty_document():
    """Test that empty or whitespace page blocks return 0 chunks without error."""
    page_blocks = [{"page_number": 1, "text": "   "}]
    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks)
    assert len(chunks) == 0

def test_very_short_document():
    """Test that short documents generate exactly 1 chunk."""
    page_blocks = [{"page_number": 1, "text": "Short contract clause."}]
    chunks = DocumentChunker.chunk_structured_pages("DOC-TEST-V1", page_blocks)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].content == "Short contract clause."

def test_large_document():
    """Test chunking performance and output for large multi-page text blocks."""
    page_blocks = [
        {"page_number": p, "text": f"ARTICLE {p}: TITLE\n\n" + "Legal text clause description. " * 50}
        for p in range(1, 15)
    ]
    chunks = DocumentChunker.chunk_structured_pages("DOC-LARGE-V1", page_blocks, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 15

def test_multiple_versions_isolation(db):
    """Test that chunks belong strictly to their respective DocumentVersion."""
    doc = Document(document_id="DOC-MULTIVER", document_name="Multiversion Test", document_type="contract")
    db.add(doc)
    db.commit()

    v1 = DocumentVersion(version_id="DOC-MULTIVER-V1_0", document_id="DOC-MULTIVER", version_number="1.0", file_name="v1.pdf", file_path="path1", file_type="pdf", file_size=100)
    v2 = DocumentVersion(version_id="DOC-MULTIVER-V2_0", document_id="DOC-MULTIVER", version_number="2.0", file_name="v2.pdf", file_path="path2", file_type="pdf", file_size=120)
    db.add_all([v1, v2])
    db.commit()

    DocumentChunker.chunk_and_store_version_chunks(db, "DOC-MULTIVER-V1_0", [{"page_number": 1, "text": "Version 1 Clause"}])
    DocumentChunker.chunk_and_store_version_chunks(db, "DOC-MULTIVER-V2_0", [{"page_number": 1, "text": "Version 2 Clause"}])

    c1 = db.query(DocumentChunk).filter(DocumentChunk.document_version_id == "DOC-MULTIVER-V1_0").all()
    c2 = db.query(DocumentChunk).filter(DocumentChunk.document_version_id == "DOC-MULTIVER-V2_0").all()

    assert len(c1) == 1
    assert len(c2) == 1
    assert "Version 1" in c1[0].content
    assert "Version 2" in c2[0].content

def test_reprocessing_without_duplicate_chunks(db):
    """Test that re-running chunking on the same version replaces existing chunks without duplicates."""
    doc = Document(document_id="DOC-REPROCESS", document_name="Reprocess Test", document_type="contract")
    db.add(doc)
    db.commit()

    v1 = DocumentVersion(version_id="DOC-REPROCESS-V1_0", document_id="DOC-REPROCESS", version_number="1.0", file_name="rep.pdf", file_path="path", file_type="pdf", file_size=100)
    db.add(v1)
    db.commit()

    # Initial chunking
    DocumentChunker.chunk_and_store_version_chunks(db, "DOC-REPROCESS-V1_0", [{"page_number": 1, "text": "Initial text block 1\n\nInitial text block 2"}])
    initial_count = db.query(DocumentChunk).filter(DocumentChunk.document_version_id == "DOC-REPROCESS-V1_0").count()

    # Reprocess
    DocumentChunker.chunk_and_store_version_chunks(db, "DOC-REPROCESS-V1_0", [{"page_number": 1, "text": "Updated text block 1"}])
    reprocessed_count = db.query(DocumentChunk).filter(DocumentChunk.document_version_id == "DOC-REPROCESS-V1_0").count()

    assert initial_count >= 1
    assert reprocessed_count == 1

def test_cascading_deletion(db):
    """Test that deleting a Document automatically cascades to delete all DocumentChunk records."""
    doc = Document(document_id="DOC-CASCADE-DEL", document_name="Cascade Delete Test", document_type="contract")
    db.add(doc)
    db.commit()

    v1 = DocumentVersion(version_id="DOC-CASCADE-DEL-V1_0", document_id="DOC-CASCADE-DEL", version_number="1.0", file_name="cas.pdf", file_path="path", file_type="pdf", file_size=100)
    db.add(v1)
    db.commit()

    DocumentChunker.chunk_and_store_version_chunks(db, "DOC-CASCADE-DEL-V1_0", [{"page_number": 1, "text": "Text to be deleted along with document"}])

    assert db.query(DocumentChunk).filter(DocumentChunk.document_version_id == "DOC-CASCADE-DEL-V1_0").count() == 1

    # Delete Document
    db.delete(doc)
    db.commit()

    # Verify chunks deleted
    assert db.query(DocumentChunk).filter(DocumentChunk.document_version_id == "DOC-CASCADE-DEL-V1_0").count() == 0
