"""
Service-layer wrapper around the RAG pipeline. This is what
chatbot_service.py calls — it never touches app.ai directly, so the
pipeline internals (Groq, Chroma, embeddings) can change without
touching the chat flow.
"""
from typing import Dict, List, Optional

from app.ai.rag_pipeline import run_rag_pipeline

FALLBACK_MESSAGE = (
    "I don't have a direct answer for that yet. I've logged your question "
    "so the ZeAI Soft team can follow up, or you can reach out to us directly."
)


def get_rag_response(query: str, chat_history: Optional[List[Dict]] = None) -> Dict:
    """
    Returns {"answer": str, "source_type": "RAG" | "Fallback", "grounded": bool}.

    "Fallback" means no relevant chunks were found in the knowledge base
    (or the Groq call failed) — chatbot_service uses this to mark the
    chat_history row's status as "fallback" instead of "resolved".
    """
    result = run_rag_pipeline(query, chat_history=chat_history)

    if result["error"]:
        return {"answer": FALLBACK_MESSAGE, "source_type": "Fallback", "grounded": False}

    if not result["grounded"]:
        return {"answer": result["answer"], "source_type": "Fallback", "grounded": False}

    return {"answer": result["answer"], "source_type": "RAG", "grounded": True}
