"""
Aggregation queries backing the admin analytics dashboard. Pulled out
of main.py so the dashboard's data shape can evolve independently of
the route definitions.
"""
from typing import List, Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models


def get_summary(db: Session) -> Dict:
    total = db.query(models.ChatHistory).count()
    faq_count = db.query(models.ChatHistory).filter(models.ChatHistory.source_type == "FAQ").count()
    rag_count = db.query(models.ChatHistory).filter(models.ChatHistory.source_type == "RAG").count()
    fallback_count = db.query(models.ChatHistory).filter(models.ChatHistory.status == "fallback").count()
    resolved_count = db.query(models.ChatHistory).filter(models.ChatHistory.status == "resolved").count()
    escalated_count = db.query(models.ChatHistory).filter(models.ChatHistory.status == "escalated").count()

    return {
        "total_chats": total,
        "faq_count": faq_count,
        "rag_count": rag_count,
        "fallback_count": fallback_count,
        "resolved_count": resolved_count,
        "escalated_count": escalated_count,
    }


def get_top_questions(db: Session, limit: int = 10) -> List[Dict]:
    results = (
        db.query(
            models.ChatHistory.user_question,
            func.count(models.ChatHistory.chat_id).label("times_asked"),
        )
        .group_by(models.ChatHistory.user_question)
        .order_by(func.count(models.ChatHistory.chat_id).desc())
        .limit(limit)
        .all()
    )
    return [{"user_question": q, "times_asked": c} for q, c in results]


def get_daily_volume(db: Session, days: int = 7) -> List[Dict]:
    results = (
        db.query(
            func.date(models.ChatHistory.created_at).label("date"),
            func.count(models.ChatHistory.chat_id).label("count"),
        )
        .group_by(func.date(models.ChatHistory.created_at))
        .order_by(func.date(models.ChatHistory.created_at).desc())
        .limit(days)
        .all()
    )
    return [{"date": str(d), "count": c} for d, c in results]


def get_recent_chat_history(db: Session, limit: int = 50) -> List[Dict]:
    logs = (
        db.query(models.ChatHistory)
        .order_by(models.ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "chat_id": log.chat_id,
            "session_id": log.session_id,
            "user_question": log.user_question,
            "bot_response": log.bot_response,
            "source_type": log.source_type,
            "status": log.status,
            "created_at": log.created_at,
        }
        for log in logs
    ]
