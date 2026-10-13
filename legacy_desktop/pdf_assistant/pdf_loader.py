"""
pdf_loader.py
--------------
Extracts raw text from a PDF file, page by page, using pypdf.
This is the first stage of the PDF question-answering pipeline:

    PDF file -> [pdf_loader] -> raw text -> [text_chunker] -> chunks
    -> [vector_store] -> relevant chunks -> [pdf_qa_engine] -> answer
"""

import os
from pypdf import PdfReader

from utils.logger import get_logger

logger = get_logger(__name__)


class PDFLoadError(Exception):
    """Raised when a PDF cannot be opened or contains no extractable text."""


class PDFLoader:
    """Reads a PDF file from disk and extracts its text content."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract all text from a PDF file, with page-boundary markers so the
        assistant can optionally reference page numbers in an answer.

        Args:
            file_path (str): Path to the .pdf file.

        Returns:
            str: Combined text of the whole document.

        Raises:
            PDFLoadError: If the file doesn't exist, isn't a PDF, or has
                no extractable text (e.g. a scanned image PDF with no OCR).
        """
        if not os.path.exists(file_path):
            raise PDFLoadError(f"File not found: {file_path}")

        if not file_path.lower().endswith(".pdf"):
            raise PDFLoadError("Only .pdf files are supported.")

        try:
            reader = PdfReader(file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF '{file_path}': {e}")
            raise PDFLoadError(f"Could not open PDF file: {e}")

        pages_text = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_number}: {e}")
                text = ""
            if text.strip():
                pages_text.append(f"[Page {page_number}]\n{text.strip()}")

        if not pages_text:
            raise PDFLoadError(
                "No extractable text found in this PDF. It may be a scanned "
                "image without OCR."
            )

        logger.info(f"Extracted text from {len(pages_text)} page(s) of '{file_path}'.")
        return "\n\n".join(pages_text)
