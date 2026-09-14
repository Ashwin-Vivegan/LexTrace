import io
import pytest 

from tests.test_extraction import create_sample_docx

def test_upload_txt_document(client):
    """Test POST /api/documents/upload with a valid text file and metadata."""
    file_content = b"LexTrace Master Services Agreement 2026\nClause 1: Scope of Services"
    files = {
        "file": ("contract.txt", file_content, "text/plain")
    }
    data = {
        "document_name": "Asterion Cloud Services Agreement",
        "document_type": "contract",
        "jurisdiction": "England and Wales",
        "practice_area": "Technology & IP",
        "client_reference": "CLIENT-881",
        "version_number": "1.0",
        "effective_date": "2026-01-15",
        "status_str": "current"
    }

    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == 201
    payload = response.json()

    assert "document_id" in payload
    assert payload["version_number"] == "1.0"
    assert payload["file_type"] == "txt"
    assert payload["text_length"] > 0
    assert payload["status"] == "current"

def test_upload_invalid_extension(client):
    """Test POST /api/documents/upload rejects invalid file extensions (e.g. .exe)."""
    files = {
        "file": ("malicious.exe", b"MZ_EXECUTABLE_HEADER", "application/octet-stream")
    }
    data = {
        "document_name": "Invalid File Test",
        "document_type": "other"
    }

    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_list_and_detail_and_versioning_flow(client):
    """
    Test full lifecycle flow:
    1. Upload document V1.0
    2. Upload document V2.0 (using existing_document_id)
    3. GET /api/documents (Verify listing)
    4. GET /api/documents/{id} (Verify versions & status updates)
    5. GET /api/documents/{id}/versions/{v}/text (Verify text endpoint)
    6. DELETE /api/documents/{id} (Verify deletion)
    """
    # 1. Upload V1.0
    v1_content = b"Version 1.0 Original Content"
    files_v1 = {"file": ("agree_v1.txt", v1_content, "text/plain")}
    data_v1 = {
        "document_name": "Multi Version Contract",
        "document_type": "contract",
        "version_number": "1.0",
        "status_str": "current"
    }
    res_v1 = client.post("/api/documents/upload", files=files_v1, data=data_v1)
    assert res_v1.status_code == 201
    doc_id = res_v1.json()["document_id"]
    v1_id = res_v1.json()["version_id"]

    # 2. Upload V2.0 referencing existing_document_id
    v2_content = b"Version 2.0 Amended & Restated Content"
    files_v2 = {"file": ("agree_v2.txt", v2_content, "text/plain")}
    data_v2 = {
        "document_name": "Multi Version Contract (Amended)",
        "document_type": "contract",
        "version_number": "2.0",
        "status_str": "current",
        "existing_document_id": doc_id
    }
    res_v2 = client.post("/api/documents/upload", files=files_v2, data=data_v2)
    assert res_v2.status_code == 201
    v2_id = res_v2.json()["version_id"]

    # 3. GET /api/documents
    res_list = client.get("/api/documents")
    assert res_list.status_code == 200
    docs = res_list.json()
    assert len(docs) >= 1
    target_doc = next(d for d in docs if d["document_id"] == doc_id)
    assert target_doc["current_version"] == "2.0"

    # 4. GET /api/documents/{document_id}
    res_detail = client.get(f"/api/documents/{doc_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert len(detail["versions"]) == 2
    
    # Check that V1 status was updated to 'superseded' and V2 status is 'current'
    v1_rec = next(v for v in detail["versions"] if v["version_id"] == v1_id)
    v2_rec = next(v for v in detail["versions"] if v["version_id"] == v2_id)
    assert v1_rec["status"] == "superseded"
    assert v2_rec["status"] == "current"

    # 5. GET /api/documents/{doc_id}/versions/{v2_id}/text
    res_text = client.get(f"/api/documents/{doc_id}/versions/{v2_id}/text")
    assert res_text.status_code == 200
    text_data = res_text.json()
    assert "Version 2.0 Amended" in text_data["text"]

    # 6. DELETE /api/documents/{doc_id}
    res_del = client.get(f"/api/documents/{doc_id}") # Confirm exists
    assert res_del.status_code == 200
    
    res_delete = client.delete(f"/api/documents/{doc_id}")
    assert res_delete.status_code == 200

    # Confirm 404 after deletion
    res_post_del = client.get(f"/api/documents/{doc_id}")
    assert res_post_del.status_code == 404
