"""
vector_store.py
------------------
A lightweight, fully offline similarity search index over text chunks,
built with scikit-learn's TF-IDF vectorizer and cosine similarity.

This avoids depending on paid embedding APIs just to find which chunks
of the PDF are relevant to a question — that part works even with no
API key configured. The AI engine (optional) is only used afterwards,
to turn the retrieved chunks into a natural-language answer.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.logger import get_logger

logger = get_logger(__name__)


class TFIDFVectorStore:
    """In-memory TF-IDF index for retrieving the most relevant text chunks."""

    def __init__(self):
        self.vectorizer = None
        self.chunk_vectors = None
        self.chunks = []

    def build(self, chunks: list):
        """
        Build (or rebuild) the TF-IDF index from a list of text chunks.

        Args:
            chunks (list[str]): Text chunks produced by text_chunker.chunk_text.
        """
        if not chunks:
            raise ValueError("Cannot build an index from an empty chunk list.")

        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.chunk_vectors = self.vectorizer.fit_transform(chunks)
        logger.info(f"Built TF-IDF index over {len(chunks)} chunk(s).")

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Find the chunks most relevant to the given query.

        Args:
            query (str): The user's question.
            top_k (int): Number of top-matching chunks to return.

        Returns:
            list[tuple[str, float]]: (chunk_text, similarity_score) pairs,
                sorted by descending relevance.
        """
        if self.vectorizer is None or self.chunk_vectors is None:
            raise RuntimeError("Index has not been built yet. Call build() first.")

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.chunk_vectors)[0]

        ranked_indices = similarities.argsort()[::-1][:top_k]
        results = [(self.chunks[i], float(similarities[i])) for i in ranked_indices]
        return results
