from pydantic import BaseModel
class ChatRequest(BaseModel):
    session_id: int
    query: str
class ChatResponse(BaseModel):
    response: str
    source: str
class SessionStartResponse(BaseModel):
    session_id: int
    session_token: str
class LoginRequest(BaseModel):
    email: str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str
from typing import Optional
class FAQCreate(BaseModel):
    category_id: int
    question: str
    answer: str
    keywords: Optional[str] = None
    display_order: int = 0
class FAQResponse(BaseModel):
    faq_id: int
    category_id: Optional[int] = None
    question: str
    answer: str
    keywords: Optional[str] = None
    display_order: int
    status: str

    class Config:
        from_attributes = True
class FAQUpdate(BaseModel):
    category_id: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    keywords: Optional[str] = None
    display_order: Optional[int] = None
    status: Optional[str] = None
class AnalyticsSummary(BaseModel):
    total_chats: int
    faq_count: int
    rag_count: int
    fallback_count: int
    resolved_count: int
    escalated_count: int
class TopQuestion(BaseModel):
    user_question: str
    times_asked: int
class DailyVolume(BaseModel):
    date: str
    count: int
from datetime import datetime
class DocumentResponse(BaseModel):
    document_id: int
    category_id: Optional[int] = None
    file_name: str
    file_type: str
    file_size: int
    embedding_status: str
    chunk_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True