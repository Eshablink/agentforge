from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.ingestion_service import DocumentIngestionService, IngestionError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=201)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> DocumentUploadResponse:
    service = DocumentIngestionService(db=db)
    try:
        document, chunk_count = service.ingest(file=file)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        status=document.status,
        chunk_count=chunk_count,
        created_at=document.created_at,
    )


@router.get("", response_model=list[DocumentListItem])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentListItem]:
    statement: Select[tuple[Document, int]] = (
        select(Document, func.count(DocumentChunk.id))
        .outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id)
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
            chunk_count=chunk_count,
            created_at=document.created_at,
        )
        for document, chunk_count in rows
    ]
