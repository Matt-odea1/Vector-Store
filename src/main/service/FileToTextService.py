"""
FileToTextService.py
Service for extracting text from PDF files (MVP).
"""
import os
from PyPDF2 import PdfReader

class FileToTextService:
    """
    Extracts text from a PDF file.
    """
    def file_to_text(self, pdf_path: str) -> str:
        """
        Extract all text from the given PDF file.
        Args:
            pdf_path (str): Path to the PDF file.
        Returns:
            str: Extracted text (empty string if unreadable).
        """
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            # TODO: Handle encrypted/image-only PDFs, log error if needed
            return ""

