"""
Orchestrates a single chat turn: try an FAQ match first (fast, free,
deterministic), fall back to the RAG pipeline, then log the exchange
to chat_history. This is the only place that decides FAQ vs RAG vs
Fallback — main.py's /chat endpoint just calls this.
"""
from typing import Dict, List

from sqlalchemy.orm import Session

from app import models
from app.services.faq_service import find_faq_match
from app.services.rag_service import get_rag_response

HISTORY_WINDOW = 4


def get_recent_history(db: Session, session_id: int, limit: int = HISTORY_WINDOW) -> List[Dict]:
    """Pulls the last few turns of this session for conversational continuity in the RAG prompt."""
    logs = (
        db.query(models.ChatHistory)
        .filter(models.ChatHistory.session_id == session_id)
        .order_by(models.ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [{"question": log.user_question, "answer": log.bot_response} for log in reversed(logs)]


def handle_chat_message(db: Session, session_id: int, query: str) -> Dict:
    matched_faq = find_faq_match(db, query)

    if matched_faq:
        answer = matched_faq.answer
        source_type = "FAQ"
        source_reference_id = matched_faq.faq_id
        category_id = matched_faq.category_id
        status = "resolved"
    else:
        history = get_recent_history(db, session_id)
        rag_result = get_rag_response(query, chat_history=history)
        answer = rag_result["answer"]
        source_type = rag_result["source_type"]
        source_reference_id = None
        category_id = None
        status = "resolved" if rag_result["grounded"] else "fallback"

    chat_log = models.ChatHistory(
        session_id=session_id,
        category_id=category_id,
        user_question=query,
        bot_response=answer,
        source_type=source_type,
        source_reference_id=source_reference_id,
        status=status,
    )
    db.add(chat_log)
    db.commit()

    return {"response": answer, "source": source_type}
