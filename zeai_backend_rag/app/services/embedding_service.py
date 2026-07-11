"""
Chunks raw document text and pushes chunks + embeddings into the
vector store. Called by document_service during ingestion — kept
separate so the chunking strategy can be tuned independently of
file handling / extraction.
"""
import uuid
from typing import List, Optional

from app.ai.embeddings import embed_texts
from app.ai import vectorstore

CHUNK_SIZE = 800   # characters per chunk
CHUNK_OVERLAP = 120  # characters shared between consecutive chunks, for context continuity


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Splits text into overlapping fixed-size chunks after normalizing whitespace."""
    text = " ".join(text.split())
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def embed_and_store_document(
    document_id: int,
    file_name: str,
    text: str,
    category_id: Optional[int] = None,
) -> int:
    """
    Chunks `text`, embeds each chunk, and upserts them into ChromaDB,
    tagged with document_id so they can be filtered or deleted later.
    Returns the number of chunks stored.
    """
    chunks = chunk_text(text)
    if not chunks:
        return 0

    ids = [f"doc{document_id}-chunk{i}-{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    embeddings = embed_texts(chunks)
    metadatas = [
        {
            "document_id": document_id,
            "source": file_name,
            "category_id": category_id or 0,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    vectorstore.upsert_chunks(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return len(chunks)


def remove_document_embeddings(document_id: int) -> None:
    vectorstore.delete_by_document(document_id)
