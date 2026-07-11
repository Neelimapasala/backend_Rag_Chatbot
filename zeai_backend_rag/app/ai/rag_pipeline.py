"""
End-to-end Retrieval-Augmented Generation pipeline:
retrieve relevant chunks -> build a grounded prompt -> ask Groq -> return
the answer plus the chunks it was grounded on.

This is the direct replacement for services/rag_placeholder.py.
"""
from typing import Dict, List, Optional

from app.ai.retriever import retrieve_chunks, build_context
from app.ai.prompt import build_rag_messages
from app.ai.groq_client import generate_chat_completion

DEFAULT_TOP_K = 4


def run_rag_pipeline(
    query: str,
    chat_history: Optional[List[Dict]] = None,
    top_k: int = DEFAULT_TOP_K,
) -> Dict:
    """
    Returns:
        {
            "answer": str,
            "chunks": List[Dict],   # what was retrieved, for citing/debugging
            "grounded": bool,       # True if at least one relevant chunk was found
            "error": bool,          # True if the Groq call itself failed
        }
    """
    chunks = retrieve_chunks(query, top_k=top_k)
    context = build_context(chunks)
    messages = build_rag_messages(query, context, chat_history)

    try:
        answer = generate_chat_completion(messages)
    except RuntimeError:
        return {
            "answer": (
                "I'm having trouble reaching the AI service right now. "
                "Please try again in a moment, or reach out to the ZeAI Soft team directly."
            ),
            "chunks": chunks,
            "grounded": False,
            "error": True,
        }

    return {
        "answer": answer,
        "chunks": chunks,
        "grounded": len(chunks) > 0,
        "error": False,
    }
