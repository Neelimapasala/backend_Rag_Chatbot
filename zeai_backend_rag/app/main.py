import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin
from app.services import (
    auth_service,
    faq_service,
    chatbot_service,
    analytics_service,
    document_service,
)

app = FastAPI(title="ZeAI Soft Chatbot API")


@app.get("/")
def root():
    return {"message": "ZeAI Soft Chatbot API is running"}


@app.get("/faqs")
def get_faqs(db: Session = Depends(get_db)):
    faqs = faq_service.list_active_faqs(db)
    return [
        {
            "faq_id": faq.faq_id,
            "question": faq.question,
            "answer": faq.answer,
            "category_id": faq.category_id,
        }
        for faq in faqs
    ]


@app.post("/session/start", response_model=schemas.SessionStartResponse)
def start_session(db: Session = Depends(get_db)):
    new_session = models.UserSession(session_token=str(uuid.uuid4()), status="active")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.session_id, "session_token": new_session.session_token}


@app.post("/admin/login", response_model=schemas.LoginResponse)
def admin_login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.login(db, request.email, request.password)
    except auth_service.InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except auth_service.InactiveAccountError:
        raise HTTPException(status_code=403, detail="Admin account is inactive")


@app.get("/admin/me")
def get_my_profile(current_admin: models.Admin = Depends(get_current_admin)):
    return {
        "admin_id": current_admin.admin_id,
        "name": current_admin.name,
        "email": current_admin.email,
        "role": current_admin.role,
    }


@app.post("/admin/faqs", response_model=schemas.FAQResponse)
def create_faq(
    faq: schemas.FAQCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    return faq_service.create_faq(db, faq, current_admin.admin_id)


@app.put("/admin/faqs/{faq_id}", response_model=schemas.FAQResponse)
def update_faq(
    faq_id: int,
    faq_update: schemas.FAQUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    faq = faq_service.update_faq(db, faq_id, faq_update)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@app.delete("/admin/faqs/{faq_id}")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    if not faq_service.delete_faq(db, faq_id):
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": f"FAQ {faq_id} marked as inactive"}


@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    return chatbot_service.handle_chat_message(db, request.session_id, request.query)


@app.get("/admin/analytics/summary", response_model=schemas.AnalyticsSummary)
def analytics_summary(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    return analytics_service.get_summary(db)


@app.get("/admin/analytics/top-questions", response_model=List[schemas.TopQuestion])
def top_questions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    return analytics_service.get_top_questions(db, limit)


@app.get("/admin/analytics/daily-volume", response_model=List[schemas.DailyVolume])
def daily_volume(
    days: int = 7,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    return analytics_service.get_daily_volume(db, days)


@app.get("/admin/chat-history")
def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    return analytics_service.get_recent_chat_history(db, limit)


# ---- Knowledge base / RAG document management ----

@app.post("/admin/documents", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    file_type = file.filename.rsplit(".", 1)[-1].lower()
    if file_type not in document_service.SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail="Only pdf, docx and txt files are supported")

    file_bytes = await file.read()
    return document_service.ingest_document(
        db, file_bytes, file.filename, file_type, category_id, current_admin.admin_id
    )


@app.get("/admin/documents", response_model=List[schemas.DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    return document_service.list_documents(db)


@app.delete("/admin/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    if not document_service.delete_document(db, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document {document_id} removed from knowledge base"}
