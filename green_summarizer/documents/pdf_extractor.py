import os
from pypdf import PdfReader
from documents.text_cleaner import TextCleaner

class PDFExtractor:
    @staticmethod
    def extract_text(filepath: str) -> dict:
        """
        Extracts text from a PDF file.
        Returns a dictionary with text, page count, and status.
        """
        if not os.path.exists(filepath):
            return {"error": "File not found", "text": "", "pages": 0}

        try:
            reader = PdfReader(filepath)
            num_pages = len(reader.pages)

            extracted_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text.append(text)

            full_text = "\n".join(extracted_text)
            cleaned_text = TextCleaner.clean(full_text)

            if len(cleaned_text.strip()) < 50 and num_pages > 0:
                return {
                    "error": "This PDF appears to be scanned or image-based. OCR support will be added in a later version.",
                    "text": cleaned_text,
                    "pages": num_pages
                }

            return {
                "error": None,
                "text": cleaned_text,
                "pages": num_pages
            }

        except Exception as e:
            return {
                "error": f"Failed to extract PDF: {str(e)}",
                "text": "",
                "pages": 0
            }
