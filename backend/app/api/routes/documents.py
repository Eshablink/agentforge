from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.auth_service import current_user
from app.services.ingestion_service import DocumentIngestionService, IngestionError

router = APIRouter(prefix="/documents", tags=["documents"])


def _list_owned_documents(db: Session, user: User) -> list[DocumentListItem]:
    statement = (
        select(Document, func.count(DocumentChunk.id))
        .outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id)
        .where(Document.user_id == user.id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )
    rows = db.execute(statement).all()
    return [
        DocumentListItem(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            status=document.status,
            chunk_count=count,
            created_at=document.created_at,
        )
        for document, count in rows
    ]


def _upload_owned_document(
    file: UploadFile,
    db: Session,
    user: User,
) -> DocumentUploadResponse:
    try:
        document, chunk_count = DocumentIngestionService(db).ingest(file=file, user_id=user.id)
    except IngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        status=document.status,
        chunk_count=chunk_count,
        created_at=document.created_at,
    )


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> DocumentUploadResponse:
    """Authenticated compatibility alias for the original upload endpoint."""
    return _upload_owned_document(file, db, user)


@router.get("", response_model=list[DocumentListItem])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[DocumentListItem]:
    """Authenticated compatibility alias; never returns another user's documents."""
    return _list_owned_documents(db, user)


@router.get("/me", response_model=list[DocumentListItem])
def list_owned_documents(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[DocumentListItem]:
    return _list_owned_documents(db, user)


@router.post("/me", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_owned_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> DocumentUploadResponse:
    return _upload_owned_document(file, db, user)
