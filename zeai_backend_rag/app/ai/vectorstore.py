"""
Persistent ChromaDB wrapper. Everything (FAQs' backing content,
company info, and uploaded knowledge-base documents) lives in one
collection so a single retrieval call can search across all of it.
"""
import os
from typing import List, Dict, Optional

import chromadb

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_store")
DEFAULT_COLLECTION = "zeai_knowledge_base"

_client = None


def get_client():
    """Lazily creates a single persistent Chroma client for the app."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def get_collection(name: str = DEFAULT_COLLECTION):
    client = get_client()
    # cosine distance works better than the default L2 for sentence embeddings
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def upsert_chunks(
    ids: List[str],
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: List[Dict],
    collection_name: str = DEFAULT_COLLECTION,
) -> None:
    """Inserts or updates chunks. IDs must be unique per chunk."""
    collection = get_collection(collection_name)
    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query(
    query_embedding: List[float],
    top_k: int = 4,
    collection_name: str = DEFAULT_COLLECTION,
    where: Optional[Dict] = None,
) -> Dict:
    collection = get_collection(collection_name)
    return collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where)


def delete_by_document(document_id: int, collection_name: str = DEFAULT_COLLECTION) -> None:
    """Removes every chunk belonging to a document, e.g. when it's deleted from the KB."""
    collection = get_collection(collection_name)
    collection.delete(where={"document_id": document_id})


def collection_count(collection_name: str = DEFAULT_COLLECTION) -> int:
    return get_collection(collection_name).count()
