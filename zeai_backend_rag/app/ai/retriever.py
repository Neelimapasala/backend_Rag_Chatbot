"""
Retrieves the most relevant knowledge-base chunks for a user query
and formats them into a single context block the LLM can be grounded on.
"""
from typing import List, Dict

from app.ai.embeddings import embed_query
from app.ai import vectorstore

DEFAULT_TOP_K = 4
MIN_RELEVANCE_SCORE = 0.25  # cosine similarity — filters out weak/irrelevant matches


def retrieve_chunks(query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
    """
    Returns a list of {"text", "score", "metadata"} dicts, best match
    first. Chroma returns cosine *distance*, so similarity = 1 - distance.
    Chunks below MIN_RELEVANCE_SCORE are dropped rather than passed to
    the LLM, so an unrelated question doesn't get a confidently wrong answer.
    """
    query_embedding = embed_query(query)
    results = vectorstore.query(query_embedding, top_k=top_k)

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    chunks = []
    for text, distance, metadata in zip(documents, distances, metadatas):
        similarity = 1 - distance
        if similarity >= MIN_RELEVANCE_SCORE:
            chunks.append({"text": text, "score": round(similarity, 4), "metadata": metadata})
    return chunks


def build_context(chunks: List[Dict]) -> str:
    """Formats retrieved chunks into a numbered, source-tagged context block."""
    if not chunks:
        return ""
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk["metadata"].get("source", "knowledge_base")
        parts.append(f"[{i}] (source: {source})\n{chunk['text']}")
    return "\n\n".join(parts)
