
import pytest

from sqlalchemy import text
from app.db.models import Document, DocumentVersion

def test_sqlite_connection(db):
    """Verify SQLite database connection and basic query execution."""
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1

def test_document_creation(db):
    """Verify logical Document model creation in SQLite via SQLAlchemy ORM."""
    doc = Document(
        document_id="DOC-TEST-001",
        document_name="Test Contract Agreement",
        document_type="contract",
        jurisdiction="New York, USA",
        practice_area="Commercial Contracts",
        client_reference="REF-1001"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    assert doc.id is not None
    assert doc.document_id == "DOC-TEST-001"
    assert doc.document_name == "Test Contract Agreement"
    assert doc.document_type == "contract"

def test_document_version_creation(db):
    """Verify Document and DocumentVersion relationship and persistence."""
    doc = Document(
        document_id="DOC-TEST-002",
        document_name="Regulatory Brief",
        document_type="regulation"
    )
    db.add(doc)
    db.commit()

    ver1 = DocumentVersion(
        version_id="DOC-TEST-002-V1",
        document_id="DOC-TEST-002",
        version_number="1.0",
        file_name="brief_v1.pdf",
        file_path="uploads/DOC-TEST-002/v1.0/brief_v1.pdf",
        file_type="pdf",
        file_size=1024,
        extracted_text="Section 1: Regulatory scope and applicability.",
        status="superseded"
    )
    ver2 = DocumentVersion(
        version_id="DOC-TEST-002-V2",
        document_id="DOC-TEST-002",
        version_number="2.0",
        file_name="brief_v2.pdf",
        file_path="uploads/DOC-TEST-002/v2.0/brief_v2.pdf",
        file_type="pdf",
        file_size=1200,
        extracted_text="Section 1 (Revised): Regulatory scope and amended applicability.",
        status="current"
    )
    db.add_all([ver1, ver2])
    db.commit()

    saved_doc = db.query(Document).filter(Document.document_id == "DOC-TEST-002").first()
    assert saved_doc is not None
    assert len(saved_doc.versions) == 2
    assert saved_doc.versions[0].version_number == "2.0"  # Ordered by ID desc
    assert saved_doc.versions[1].version_number == "1.0"

def test_document_cascading_deletion(db):
    """Verify deleting a Document automatically cascades to delete all associated DocumentVersion records."""
    doc = Document(document_id="DOC-TEST-DEL", document_name="Delete Test Doc", document_type="other")
    db.add(doc)
    db.commit()

    ver = DocumentVersion(
        version_id="DOC-TEST-DEL-V1",
        document_id="DOC-TEST-DEL",
        version_number="1.0",
        file_name="del.txt",
        file_path="uploads/DOC-TEST-DEL/v1.0/del.txt",
        file_type="txt",
        file_size=100,
        extracted_text="Text to be deleted"
    )
    db.add(ver)
    db.commit()

    # Delete Document
    db.delete(doc)
    db.commit()

    # Verify version record is also deleted
    orphan_ver = db.query(DocumentVersion).filter(DocumentVersion.version_id == "DOC-TEST-DEL-V1").first()
    assert orphan_ver is None
