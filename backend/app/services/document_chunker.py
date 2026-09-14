import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import DocumentChunk, DocumentVersion

# Regex patterns for detecting legal section and subsection headings
SECTION_HEADING_PATTERN = re.compile(
    r'^(?:'
    r'(?:SECTION|ARTICLE|CLAUSE|EXHIBIT|SCHEDULE|ATTACHMENT|TITLE)\s+[0-9A-Z._-]+.*|'
    r'(?:[0-9]{1,2}\.[0-9]{0,2}\b)\s+[A-Z].*|'
    r'^[A-Z0-9\s.,\-\:\;]{4,80}:$'
    r')',
    re.IGNORECASE
)

SUBSECTION_HEADING_PATTERN = re.compile(
    r'^(?:'
    r'\([a-z0-9]{1,3}\)\s+.*|'
    r'[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,3}\s+.*'
    r')',
    re.IGNORECASE
)

def parse_heading(line: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Analyzes a line of text to determine if it is a section or subsection heading.
    Returns (section_name, subsection_name).
    """
    clean_line = line.strip()
    if not clean_line or len(clean_line) > 150:
        return None, None

    if SECTION_HEADING_PATTERN.match(clean_line):
        return clean_line, None
    elif SUBSECTION_HEADING_PATTERN.match(clean_line):
        return None, clean_line
    return None, None

class DocumentChunker:
    """
    Service responsible for structure-aware, deterministic text chunking,
    overlap handling, section metadata extraction, and transactional persistence in SQLite.
    """

    @classmethod
    def chunk_structured_pages(
        cls,
        version_id: str,
        page_blocks: List[Dict[str, Any]],
        chunk_size: int = settings.CHUNK_SIZE_CHARS,
        chunk_overlap: int = settings.CHUNK_OVERLAP_CHARS
    ) -> List[DocumentChunk]:
        """
        Splits structured page blocks into sequential DocumentChunk model instances.
        Preserves structural metadata (section_name, subsection_name, page_number)
        and applies character-based overlap between adjacent chunks.
        """
        chunks: List[DocumentChunk] = []
        chunk_index = 0
        global_char_offset = 0

        active_section: Optional[str] = None
        active_subsection: Optional[str] = None

        for block in page_blocks:
            page_num = block.get("page_number")
            raw_text = block.get("text", "").strip()
            if not raw_text:
                continue

            # Split page content into structural paragraphs
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', raw_text) if p.strip()]

            current_buffer: List[str] = []
            current_buffer_len = 0
            buffer_start_offset = global_char_offset

            for para in paragraphs:
                # Check for section/subsection heading updates
                sec_found, subsec_found = parse_heading(para)
                if sec_found:
                    active_section = sec_found
                    active_subsection = None
                elif subsec_found:
                    active_subsection = subsec_found

                para_len = len(para)

                # If adding this paragraph exceeds target chunk size and buffer is non-empty, finalize chunk
                if current_buffer_len > 0 and (current_buffer_len + para_len + 2 > chunk_size):
                    chunk_text = "\n\n".join(current_buffer).strip()
                    char_start = buffer_start_offset
                    char_end = char_start + len(chunk_text)

                    chunk_id = f"{version_id}-CHK-{(chunk_index + 1):04d}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        document_version_id=version_id,
                        chunk_index=chunk_index,
                        content=chunk_text,
                        section_name=active_section,
                        subsection_name=active_subsection,
                        page_number=page_num,
                        character_start=char_start,
                        character_end=char_end
                    ))
                    chunk_index += 1

                    # Apply overlap: take trailing characters from current_buffer
                    overlap_text = chunk_text[-chunk_overlap:] if len(chunk_text) > chunk_overlap else chunk_text
                    current_buffer = [overlap_text, para]
                    current_buffer_len = len(overlap_text) + 2 + para_len
                    buffer_start_offset = max(0, char_end - len(overlap_text))
                else:
                    current_buffer.append(para)
                    current_buffer_len += para_len + 2

                global_char_offset += para_len + 2

            # Flush remaining buffer at the end of the block
            if current_buffer:
                chunk_text = "\n\n".join(current_buffer).strip()
                if chunk_text:
                    char_start = buffer_start_offset
                    char_end = char_start + len(chunk_text)
                    chunk_id = f"{version_id}-CHK-{(chunk_index + 1):04d}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        document_version_id=version_id,
                        chunk_index=chunk_index,
                        content=chunk_text,
                        section_name=active_section,
                        subsection_name=active_subsection,
                        page_number=page_num,
                        character_start=char_start,
                        character_end=char_end
                    ))
                    chunk_index += 1

        return chunks

    @classmethod
    def chunk_and_store_version_chunks(
        cls,
        db: Session,
        version_id: str,
        page_blocks: List[Dict[str, Any]],
        chunk_size: int = settings.CHUNK_SIZE_CHARS,
        chunk_overlap: int = settings.CHUNK_OVERLAP_CHARS
    ) -> List[DocumentChunk]:
        """
        Safely processes text into chunks and stores them in SQLite inside a single database transaction.
        Reprocessing Safety: Deletes any pre-existing chunks for this version_id before creating new ones.
        """
        # 1. Reprocessing Safety: Delete existing chunks for this version_id
        db.query(DocumentChunk).filter(DocumentChunk.document_version_id == version_id).delete(synchronize_session=False)

        # 2. Generate chunks
        chunks = cls.chunk_structured_pages(
            version_id=version_id,
            page_blocks=page_blocks,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # 3. Bulk insert and commit
        if chunks:
            db.add_all(chunks)

        db.flush()
        return chunks
