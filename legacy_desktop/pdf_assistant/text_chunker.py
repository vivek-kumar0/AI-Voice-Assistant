"""
text_chunker.py
-----------------
Splits long PDF text into overlapping chunks small enough to be scored
individually against a user's question. Overlap prevents an answer-bearing
sentence from being cut in half between two chunks.
"""

from utils.logger import get_logger

logger = get_logger(__name__)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list:
    """
    Split text into overlapping word-based chunks.

    Args:
        text (str): Full document text.
        chunk_size (int): Approximate number of words per chunk.
        overlap (int): Number of words repeated between consecutive chunks,
            so context isn't lost at chunk boundaries.

    Returns:
        list[str]: List of text chunks.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap  # step forward, but re-include the overlap

    logger.info(f"Split document into {len(chunks)} chunk(s).")
    return chunks
