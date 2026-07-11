"""
Prompt templates for the RAG pipeline. Kept separate from the
pipeline logic so the persona and grounding rules can be tuned
without touching retrieval or the Groq call.
"""
from typing import List, Dict, Optional

SYSTEM_PROMPT = """You are the official AI assistant for ZeAI Soft, an AI/software \
solutions company based in Chennai, founded by Kirthika K. \
Answer the user's question using ONLY the context provided below. \
If the context does not contain the answer, say clearly that you don't \
have that information yet and suggest the user contact the ZeAI Soft team \
directly — never invent facts about the company, its services, or its people. \
Keep answers concise, friendly, and professional. Do not mention that you \
were given "context" — just answer naturally as ZeAI Soft's assistant."""


def build_rag_messages(
    query: str,
    context: str,
    chat_history: Optional[List[Dict]] = None,
) -> List[Dict[str, str]]:
    """
    Builds the full message list sent to Groq: system persona, a short
    window of recent turns for continuity, then the grounded question.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for turn in (chat_history or [])[-4:]:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})

    if context:
        user_content = f"Context:\n{context}\n\nQuestion: {query}"
    else:
        user_content = (
            f"Question: {query}\n\n"
            "(No relevant context was found in the knowledge base — "
            "let the user know politely and don't guess.)"
        )

    messages.append({"role": "user", "content": user_content})
    return messages
