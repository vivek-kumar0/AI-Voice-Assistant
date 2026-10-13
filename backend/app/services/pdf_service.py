from pathlib import Path
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunks(text: str, size: int = 1200, overlap: int = 150):
    text = " ".join(text.split())
    if not text:
        return []
    out = []
    step = max(1, size - overlap)
    for i in range(0, len(text), step):
        part = text[i:i+size]
        if part:
            out.append(part)
        if i + size >= len(text):
            break
    return out

def search(text: str, query: str, top_k: int = 4) -> list[tuple[str, float]]:
    items = chunks(text)
    if not items:
        return []
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(items)
    q = vectorizer.transform([query])
    scores = cosine_similarity(q, matrix)[0]
    idx = scores.argsort()[::-1][:top_k]
    return [(items[i], float(scores[i])) for i in idx]
