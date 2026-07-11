"""
FAQ matching + CRUD. The matching logic is the same keyword-overlap
approach that was in services/faq_matcher.py, now living behind a
service so main.py and chatbot_service.py both call it consistently.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas

MIN_MATCH_SCORE = 2
MIN_WORD_LENGTH = 3


def find_faq_match(db: Session, user_query: str) -> Optional[models.FAQ]:
    """Scores active FAQs by shared keywords with the query, returns the best match if it clears the threshold."""
    query_words = {w.strip().lower() for w in user_query.split() if len(w) > MIN_WORD_LENGTH}
    if not query_words:
        return None

    faqs = db.query(models.FAQ).filter(models.FAQ.status == "active").all()

    best_match, best_score = None, 0
    for faq in faqs:
        question_words = set(faq.question.lower().split())
        score = len(query_words & question_words)
        if score > best_score:
            best_score, best_match = score, faq

    return best_match if best_score >= MIN_MATCH_SCORE else None


def create_faq(db: Session, faq: schemas.FAQCreate, admin_id: int) -> models.FAQ:
    new_faq = models.FAQ(
        category_id=faq.category_id,
        question=faq.question,
        answer=faq.answer,
        keywords=faq.keywords,
        display_order=faq.display_order,
        created_by=admin_id,
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq


def update_faq(db: Session, faq_id: int, faq_update: schemas.FAQUpdate) -> Optional[models.FAQ]:
    faq = db.query(models.FAQ).filter(models.FAQ.faq_id == faq_id).first()
    if not faq:
        return None

    for field, value in faq_update.model_dump(exclude_unset=True).items():
        setattr(faq, field, value)

    db.commit()
    db.refresh(faq)
    return faq


def delete_faq(db: Session, faq_id: int) -> bool:
    faq = db.query(models.FAQ).filter(models.FAQ.faq_id == faq_id).first()
    if not faq:
        return False
    faq.status = "inactive"
    db.commit()
    return True


def list_active_faqs(db: Session) -> List[models.FAQ]:
    return db.query(models.FAQ).filter(models.FAQ.status == "active").all()
