"""
Thin wrapper around the Groq Chat Completions API.

Centralizes model selection, the API key, and error handling so the
rest of the RAG pipeline never talks to the Groq SDK directly — if
Groq changes their SDK or you swap models later, this is the only
file that needs to change.
"""
import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client: Optional[Groq] = None


def get_client() -> Groq:
    """Lazily creates a single shared Groq client for the app's lifetime."""
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file: "
                "GROQ_API_KEY=your_key_here"
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def generate_chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 600,
    model: Optional[str] = None,
) -> str:
    """
    Sends a list of {"role": "system"|"user"|"assistant", "content": str}
    messages to Groq and returns the assistant's reply text.

    Raises RuntimeError on any failure so callers can decide how to
    degrade gracefully (e.g. fall back to a canned response).
    """
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model or GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        raise RuntimeError(f"Groq API call failed: {exc}") from exc
