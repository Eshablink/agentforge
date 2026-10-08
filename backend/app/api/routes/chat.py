from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.auth_service import current_user
from app.services.rag_service import RAGService, RAGServiceError

router = APIRouter(tags=["chat"])


def _answer(payload: ChatRequest, db: Session, user: User) -> ChatResponse:
    service = RAGService(db=db)
    try:
        return service.answer(question=payload.question, top_k=payload.top_k, user_id=user.id)
    except RAGServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse)
def ask_question(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ChatResponse:
    """Authenticated compatibility alias for the original chat endpoint."""
    return _answer(payload, db, user)


@router.post("/me/chat", response_model=ChatResponse)
def ask_owned_question(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ChatResponse:
    return _answer(payload, db, user)
