import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../green_summarizer')))

from documents.text_cleaner import TextCleaner
from documents.chunker import DocumentChunker
from documents.pdf_extractor import PDFExtractor
from fpdf import FPDF
import pytest

def test_text_cleaner():
    raw_text = "This   has \n\n\n multiple spaces and a URL https://example.com"
    cleaned = TextCleaner.clean(raw_text)
    assert cleaned == "This has \n\n multiple spaces and a URL"

def test_document_chunker():
    long_text = "Word " * 600
    chunks = DocumentChunker.chunk_text(long_text, max_words_per_chunk=500)
    assert len(chunks) == 2
    assert len(chunks[0].split()) == 500
    assert len(chunks[1].split()) == 100

def test_pdf_extractor(tmp_path):
    pdf_path = tmp_path / "test_dummy.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a test PDF document.", ln=1, align="C")
    # Add more text so it bypasses the 50 char OCR warning limit in PDFExtractor
    pdf.cell(200, 10, txt="Adding more text so the extractor does not think this is an empty scanned image file.", ln=1, align="C")
    pdf.output(str(pdf_path))

    result = PDFExtractor.extract_text(str(pdf_path))
    assert result['error'] is None
    assert "This is a test PDF document" in result['text']
    assert result['pages'] == 1
