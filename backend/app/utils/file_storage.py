import os
import re
import shutil
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filenames to prevent path traversal attacks and OS filesystem errors.
    Removes path separators and restricts to safe characters.
    """
    # Extract basename to strip out directory component attempts
    base = os.path.basename(filename)
    # Replace non-alphanumeric (except dots, dashes, underscores) with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    if not sanitized or sanitized in ('.', '..'):
        sanitized = "uploaded_file"
    return sanitized

def get_version_directory(document_id: str, version_number: str) -> str:
    """
    Constructs and creates the directory path for a specific document version:
    uploads/<document_id>/v<version_number>/
    """
    safe_doc_id = sanitize_filename(document_id)
    safe_v_num = re.sub(r'[^a-zA-Z0-9._-]', '', version_number) or "1.0"
    
    dir_path = os.path.join(settings.UPLOAD_DIR, safe_doc_id, f"v{safe_v_num}")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

async def save_uploaded_file(file: UploadFile, document_id: str, version_number: str) -> Tuple[str, str, int]:
    """
    Saves an uploaded file stream safely to disk under uploads/<document_id>/v<version_number>/<filename>.
    Enforces maximum file size limit (25 MB).
    Returns (relative_file_path, absolute_file_path, file_size_bytes).
    """
    safe_name = sanitize_filename(file.filename or "file")
    target_dir = get_version_directory(document_id, version_number)
    abs_file_path = os.path.join(target_dir, safe_name)
    
    size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        with open(abs_file_path, "wb") as f:
            while chunk := await file.read(chunk_size):
                size += len(chunk)
                if size > settings.MAX_UPLOAD_SIZE_BYTES:
                    # Clean up file partially written
                    f.close()
                    if os.path.exists(abs_file_path):
                        os.remove(abs_file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)} MB."
                    )
                f.write(chunk)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file to disk: {str(e)}"
        )
    
    # Store normalized relative path in database for portability
    rel_file_path = os.path.relpath(abs_file_path, start=".")
    return rel_file_path, abs_file_path, size

def delete_document_directory(document_id: str) -> bool:
    """
    Safely deletes the upload directory tree for a document (uploads/<document_id>/).
    Prevents path traversal by ensuring the target directory is within UPLOAD_DIR.
    """
    safe_doc_id = sanitize_filename(document_id)
    doc_dir = os.path.abspath(os.path.join(settings.UPLOAD_DIR, safe_doc_id))
    upload_root = os.path.abspath(settings.UPLOAD_DIR)
    
    # Ensure doc_dir is strictly inside upload_root to prevent accidental directory traversal deletion
    if not doc_dir.startswith(upload_root) or doc_dir == upload_root:
        return False

    if os.path.exists(doc_dir) and os.path.isdir(doc_dir):
        shutil.rmtree(doc_dir, ignore_errors=True)
        return True
    return False
