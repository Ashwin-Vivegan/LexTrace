import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Document, DocumentVersion, DocumentChunk
from app.core.config import settings
from app.schemas.document import (
    DocumentMetadataInput,
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDetailResponse,
    DocumentVersionResponse,
    ExtractedTextResponse,
    DocumentChunkResponse,
    DocumentChunkListResponse
)
from app.utils.file_storage import save_uploaded_file, delete_document_directory
from app.services.document_extractor import DocumentExtractor, ExtractionError
from app.services.document_chunker import DocumentChunker

router = APIRouter(prefix="/documents", tags=["Documents"])

def generate_document_id(db: Session) -> str:
    """Generates a clean unique document identifier (e.g. DOC-001, DOC-002, or DOC-<hash>)."""
    count = db.query(Document).count()
    short_uuid = uuid.uuid4().hex[:4].upper()
    return f"DOC-{count + 101}-{short_uuid}"

def generate_version_id(doc_id: str, version_num: str) -> str:
    v_clean = version_num.replace(".", "_")
    return f"{doc_id}-V{v_clean}"

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_name: str = Form(...),
    document_type: str = Form("other"),
    jurisdiction: Optional[str] = Form(None),
    practice_area: Optional[str] = Form(None),
    client_reference: Optional[str] = Form(None),
    version_number: str = Form("1.0"),
    effective_date: Optional[str] = Form(None),
    status_str: str = Form("current"),
    existing_document_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingests a legal document (.pdf, .docx, .txt), extracts text, breaks text into structure-aware chunks,
    stores physical version files, and creates Document, DocumentVersion, and DocumentChunk DB records.
    """
    # 1. Validate file extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    file_type = file_ext.lstrip(".")

    # 2. Validate metadata input via Pydantic model
    try:
        meta = DocumentMetadataInput(
            document_name=document_name,
            document_type=document_type,
            jurisdiction=jurisdiction,
            practice_area=practice_area,
            client_reference=client_reference,
            version_number=version_number,
            effective_date=effective_date,
            status=status_str,
            existing_document_id=existing_document_id
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))

    # 3. Handle Document creation or retrieval
    if meta.existing_document_id:
        doc = db.query(Document).filter(Document.document_id == meta.existing_document_id).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{meta.existing_document_id}' not found."
            )
        doc_id = doc.document_id
        doc.document_name = meta.document_name
        doc.document_type = meta.document_type
        if meta.jurisdiction:
            doc.jurisdiction = meta.jurisdiction
        if meta.practice_area:
            doc.practice_area = meta.practice_area
        if meta.client_reference:
            doc.client_reference = meta.client_reference
    else:
        doc_id = generate_document_id(db)
        doc = Document(
            document_id=doc_id,
            document_name=meta.document_name,
            document_type=meta.document_type,
            jurisdiction=meta.jurisdiction,
            practice_area=meta.practice_area,
            client_reference=meta.client_reference
        )
        db.add(doc)
        db.flush()

    # 4. Check version ID uniqueness
    version_id = generate_version_id(doc_id, meta.version_number)
    existing_version = db.query(DocumentVersion).filter(DocumentVersion.version_id == version_id).first()
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Version '{meta.version_number}' (ID: {version_id}) already exists for document '{doc_id}'."
        )

    # 5. Save uploaded file to disk
    rel_path, abs_path, file_size = await save_uploaded_file(file, doc_id, meta.version_number)

    # 6. Extract structured page blocks and full text
    try:
        page_blocks = DocumentExtractor.extract_structured_pages(abs_path, file_type)
        extracted_text = "\n\n".join(b["text"] for b in page_blocks if b.get("text"))
    except ExtractionError as ext_err:
        if os.path.exists(abs_path):
            os.remove(abs_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ext_err))

    # 7. Update status of existing versions if this version is marked 'current'
    if meta.status == "current":
        db.query(DocumentVersion).filter(
            DocumentVersion.document_id == doc_id,
            DocumentVersion.status == "current"
        ).update({"status": "superseded"}, synchronize_session=False)

    # 8. Create new DocumentVersion record
    new_version = DocumentVersion(
        version_id=version_id,
        document_id=doc_id,
        version_number=meta.version_number,
        file_name=file.filename or f"doc_{version_id}.{file_type}",
        file_path=rel_path,
        file_type=file_type,
        file_size=file_size,
        extracted_text=extracted_text,
        effective_date=meta.effective_date,
        status=meta.status
    )
    db.add(new_version)
    db.flush()

    # 9. Perform Structure-Aware Document Chunking
    chunks = DocumentChunker.chunk_and_store_version_chunks(
        db=db,
        version_id=version_id,
        page_blocks=page_blocks
    )

    try:
        db.commit()
        db.refresh(new_version)
    except Exception as db_err:
        db.rollback()
        if os.path.exists(abs_path):
            os.remove(abs_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database commit error: {str(db_err)}"
        )

    return DocumentUploadResponse(
        document_id=doc_id,
        version_id=version_id,
        document_name=doc.document_name,
        document_type=doc.document_type,
        version_number=new_version.version_number,
        status=new_version.status,
        file_type=new_version.file_type,
        file_size=new_version.file_size,
        text_length=len(extracted_text or ""),
        chunk_count=len(chunks),
        message="Document uploaded and processed successfully"
    )

@router.get("", response_model=List[DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    """
    Returns a list of logical documents with high-level metadata and current version status.
    Excludes full extracted text to keep responses lightweight.
    """
    docs = db.query(Document).order_by(Document.updated_at.desc()).all()
    results = []
    
    for doc in docs:
        current_v = next((v for v in doc.versions if v.status == "current"), None)
        latest_v = current_v or (doc.versions[0] if doc.versions else None)
        
        results.append(DocumentListItem(
            document_id=doc.document_id,
            document_name=doc.document_name,
            document_type=doc.document_type,
            jurisdiction=doc.jurisdiction,
            practice_area=doc.practice_area,
            client_reference=doc.client_reference,
            current_version=latest_v.version_number if latest_v else None,
            status=latest_v.status if latest_v else None,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        ))
    return results

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_detail(document_id: str, db: Session = Depends(get_db)):
    """
    Returns detailed metadata for a document along with all associated versions and chunk counts.
    """
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )

    current_v = next((v for v in doc.versions if v.status == "current"), None)
    
    versions_resp = [
        DocumentVersionResponse(
            version_id=v.version_id,
            version_number=v.version_number,
            status=v.status,
            file_name=v.file_name,
            file_type=v.file_type,
            file_size=v.file_size,
            text_length=len(v.extracted_text or ""),
            chunk_count=len(v.chunks),
            effective_date=v.effective_date,
            created_at=v.created_at
        ) for v in doc.versions
    ]

    return DocumentDetailResponse(
        document_id=doc.document_id,
        document_name=doc.document_name,
        document_type=doc.document_type,
        jurisdiction=doc.jurisdiction,
        practice_area=doc.practice_area,
        client_reference=doc.client_reference,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        current_version=current_v.version_number if current_v else None,
        versions=versions_resp
    )

@router.get("/{document_id}/versions/{version_id}/text", response_model=ExtractedTextResponse)
def get_extracted_text(document_id: str, version_id: str, db: Session = Depends(get_db)):
    """
    Returns the full extracted text for a specific document version (for development/testing).
    """
    version = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.version_id == version_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version '{version_id}' for document '{document_id}' not found."
        )

    return ExtractedTextResponse(
        document_id=document_id,
        version_id=version_id,
        text=version.extracted_text or ""
    )

@router.get("/{document_id}/versions/{version_id}/chunks", response_model=DocumentChunkListResponse)
def get_version_chunks(
    document_id: str,
    version_id: str,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Returns sequential, paginated DocumentChunks for a specific DocumentVersion.
    Preserves original index ordering and structural metadata (section, page).
    """
    version = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.version_id == version_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version '{version_id}' for document '{document_id}' not found."
        )

    query = db.query(DocumentChunk).filter(
        DocumentChunk.document_version_id == version_id
    ).order_by(DocumentChunk.chunk_index.asc())

    total_chunks = query.count()
    chunks = query.offset((page - 1) * limit).limit(limit).all()

    chunk_responses = [
        DocumentChunkResponse(
            chunk_id=c.chunk_id,
            chunk_index=c.chunk_index,
            section_name=c.section_name,
            subsection_name=c.subsection_name,
            page_number=c.page_number,
            character_start=c.character_start,
            character_end=c.character_end,
            content=c.content
        ) for c in chunks
    ]

    return DocumentChunkListResponse(
        document_id=document_id,
        version_id=version_id,
        total_chunks=total_chunks,
        page=page,
        limit=limit,
        chunks=chunk_responses
    )

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Deletes the logical document, all database version and chunk records, and physical files on disk.
    """
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )

    # 1. Remove physical files from disk
    delete_document_directory(document_id)

    # 2. Delete database records (cascades to DocumentVersion and DocumentChunk)
    db.delete(doc)
    db.commit()

    return {
        "success": True,
        "document_id": document_id,
        "message": f"Document '{document_id}' and all associated versions/chunks were successfully deleted."
    }
