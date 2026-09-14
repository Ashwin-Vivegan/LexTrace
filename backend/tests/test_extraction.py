import io
import os
#
import pytest  # Ensure pytest is installed

import pypdf
import docx
from app.services.document_extractor import DocumentExtractor, ExtractionError

def create_sample_pdf(content: str = "This is a test legal agreement clause.") -> bytes:
    """Helper to generate a valid PDF byte stream containing text using pypdf."""
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    
    # We can write simple PDF annotations or text stream
    # pypdf Writer doesn't have high-level drawing without canvas, but we can write plain PDF object text stream
    # Alternatively, create a standard minimal PDF string structure or add page content
    buffer = io.BytesIO()
    writer.write(buffer)
    # Return minimal valid PDF byte content
    pdf_bytes = buffer.getvalue()
    return pdf_bytes

def create_sample_docx(content: str = "Master Services Agreement Clause 1.1") -> bytes:
    """Helper to generate a valid DOCX byte stream using python-docx."""
    doc = docx.Document()
    doc.add_heading("Legal Agreement", level=1)
    doc.add_paragraph(content)
    
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Term"
    hdr_cells[1].text = "Definition"
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def test_txt_extraction(tmp_path):
    """Test text extraction from a valid TXT file."""
    txt_file = tmp_path / "sample.txt"
    sample_text = "LexTrace Document Intelligence Test\nClause 1: Governing Law\nThis agreement is governed by laws of England & Wales."
    txt_file.write_text(sample_text, encoding="utf-8")

    extracted = DocumentExtractor.extract_text(str(txt_file), "txt")
    assert "Governing Law" in extracted
    assert "England & Wales" in extracted

def test_docx_extraction(tmp_path):
    """Test text extraction from a valid DOCX file."""
    docx_file = tmp_path / "sample.docx"
    docx_bytes = create_sample_docx("This agreement specifies indemnity obligations.")
    docx_file.write_bytes(docx_bytes)

    extracted = DocumentExtractor.extract_text(str(docx_file), "docx")
    assert "Legal Agreement" in extracted
    assert "indemnity obligations" in extracted
    assert "Term" in extracted

def test_empty_file_rejection(tmp_path):
    """Test that zero-byte files raise an ExtractionError."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_bytes(b"")

    with pytest.raises(ExtractionError, match="Uploaded file is empty"):
        DocumentExtractor.extract_text(str(empty_file), "txt")

def test_invalid_magic_bytes_rejection(tmp_path):
    """Test that fake PDF files with spoofed extensions are rejected by header validation."""
    fake_pdf = tmp_path / "spoofed.pdf"
    fake_pdf.write_bytes(b"THIS_IS_NOT_A_REAL_PDF_HEADER")

    with pytest.raises(ExtractionError, match="Invalid PDF file format"):
        DocumentExtractor.extract_text(str(fake_pdf), "pdf")
