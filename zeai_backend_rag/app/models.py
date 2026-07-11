from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, DateTime,
    Enum, DECIMAL, ForeignKey, Boolean
)
from sqlalchemy.sql import func
from app.database import Base


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("super_admin", "admin"), default="admin", nullable=False)
    status = Column(Enum("active", "inactive"), default="active", nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum("active", "inactive"), default="active", nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class FAQ(Base):
    __tablename__ = "faqs"

    faq_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    status = Column(Enum("active", "inactive"), default="active", nullable=False)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    chat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    user_question = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    source_type = Column(
        Enum("FAQ", "RAG", "Company Content", "Fallback"), nullable=False
    )
    source_reference_id = Column(Integer, nullable=True)
    response_time = Column(DECIMAL(6, 3), nullable=True)
    feedback_score = Column(Integer, nullable=True)
    status = Column(
        Enum("resolved", "fallback", "escalated"), default="resolved", nullable=False
    )
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(Enum("pdf", "docx", "txt"), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("admin.admin_id"), nullable=True)
    embedding_model = Column(String(100), nullable=True)
    embedding_status = Column(
        Enum("pending", "processing", "completed", "failed"),
        default="pending",
        nullable=False,
    )
    chunk_count = Column(Integer, default=0)
    is_searchable = Column(Boolean, default=True)
    vector_collection = Column(String(100), nullable=True)
    status = Column(Enum("active", "inactive"), default="active", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_token = Column(String(255), nullable=False, unique=True)
    user_name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum("active", "ended"), default="active", nullable=False)