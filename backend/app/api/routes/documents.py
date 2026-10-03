from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.auth_service import current_user
from app.services.ingestion_service import DocumentIngestionService, IngestionError

router = APIRouter(prefix="/documents", tags=["documents"])
_optional_bearer = HTTPBearer(auto_error=False)


@router.post("", response_model=DocumentUploadResponse, status_code=201)
def upload_document(file=__import__("fastapi").File(...), db: Session = Depends(get_db)) -> DocumentUploadResponse:
    # Compatibility route remains available; authenticated uploads should use /me/documents/upload.
    service = DocumentIngestionService(db=db)
    try:
        document, chunk_count = service.ingest(file=file)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DocumentUploadResponse(id=document.id, filename=document.filename, content_type=document.content_type, status=document.status, chunk_count=chunk_count, created_at=document.created_at)


@router.get("", response_model=list[DocumentListItem])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentListItem]:
    statement = (select(Document, func.count(DocumentChunk.id)).outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id).where(Document.user_id.is_(None)).group_by(Document.id).order_by(Document.created_at.desc()))
    rows = db.execute(statement).all()
    return [DocumentListItem(id=d.id, filename=d.filename, content_type=d.content_type, status=d.status, chunk_count=count, created_at=d.created_at) for d, count in rows]


@router.get("/me", response_model=list[DocumentListItem])
def list_owned_documents(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[DocumentListItem]:
    statement = (select(Document, func.count(DocumentChunk.id)).outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id).where(Document.user_id == user.id).group_by(Document.id).order_by(Document.created_at.desc()))
    rows = db.execute(statement).all()
    return [DocumentListItem(id=d.id, filename=d.filename, content_type=d.content_type, status=d.status, chunk_count=count, created_at=d.created_at) for d, count in rows]


@router.post("/me", response_model=DocumentUploadResponse, status_code=201)
def upload_owned_document(file=__import__("fastapi").File(...), db: Session = Depends(get_db), user: User = Depends(current_user)) -> DocumentUploadResponse:
    try:
        document, chunk_count = DocumentIngestionService(db).ingest(file, user_id=user.id)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DocumentUploadResponse(id=document.id, filename=document.filename, content_type=document.content_type, status=document.status, chunk_count=chunk_count, created_at=document.created_at)
