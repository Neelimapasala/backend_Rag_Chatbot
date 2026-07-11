"""
Handles knowledge-base document ingestion: saving the upload, extracting
text (pdf/docx/txt), chunking + embedding it, and keeping the
KnowledgeBase table in sync with the vector store.
"""
import os
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from app import models
from app.services.embedding_service import embed_and_store_document, remove_document_embeddings

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads/knowledge_base"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_TYPES = ("pdf", "docx", "txt")


def extract_text(file_path: Path, file_type: str) -> str:
    if file_type == "txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")

    if file_type == "pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if file_type == "docx":
        import docx
        doc = docx.Document(str(file_path))
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Unsupported file type: {file_type}")


def save_uploaded_file(file_bytes: bytes, file_name: str) -> Path:
    destination = UPLOAD_DIR / file_name
    destination.write_bytes(file_bytes)
    return destination


def ingest_document(
    db: Session,
    file_bytes: bytes,
    file_name: str,
    file_type: str,
    category_id: int,
    uploaded_by: int,
) -> models.KnowledgeBase:
    """
    Saves the file, creates a KnowledgeBase row with status "processing",
    extracts + embeds the text, then updates the row to "completed" or
    "failed". A bad file never raises past this point — it just leaves
    the row marked "failed" for the admin panel to show.
    """
    file_path = save_uploaded_file(file_bytes, file_name)

    kb_entry = models.KnowledgeBase(
        category_id=category_id,
        file_name=file_name,
        file_path=str(file_path),
        file_type=file_type,
        file_size=len(file_bytes),
        uploaded_by=uploaded_by,
        embedding_model="all-MiniLM-L6-v2",
        embedding_status="processing",
        vector_collection="zeai_knowledge_base",
    )
    db.add(kb_entry)
    db.commit()
    db.refresh(kb_entry)

    try:
        text = extract_text(file_path, file_type)
        chunk_count = embed_and_store_document(
            document_id=kb_entry.document_id,
            file_name=file_name,
            text=text,
            category_id=category_id,
        )
        kb_entry.embedding_status = "completed" if chunk_count else "failed"
        kb_entry.chunk_count = chunk_count
    except Exception:
        kb_entry.embedding_status = "failed"

    db.commit()
    db.refresh(kb_entry)
    return kb_entry


def delete_document(db: Session, document_id: int) -> bool:
    """Soft-deletes the KB row and removes its chunks from the vector store."""
    kb_entry = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.document_id == document_id).first()
    if not kb_entry:
        return False

    remove_document_embeddings(document_id)
    kb_entry.status = "inactive"
    kb_entry.is_searchable = False
    db.commit()
    return True


def list_documents(db: Session) -> List[models.KnowledgeBase]:
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.status == "active").all()
