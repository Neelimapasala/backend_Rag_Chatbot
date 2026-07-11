"""
Generates vector embeddings for text using a local sentence-transformers
model. Kept separate from Groq deliberately — Groq doesn't serve an
embeddings endpoint, and running embeddings locally means document
ingestion has no external API cost or rate limit.
"""
from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

# Small, fast, and good enough for FAQ/company-content style retrieval.
# Swap this for a bigger model later if recall quality needs it.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Loads the model once per process and reuses it (loading is slow)."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embeds a batch of chunks. Returns [] for an empty input list."""
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(query: str) -> List[float]:
    """Convenience wrapper for embedding a single user query."""
    return embed_texts([query])[0]
