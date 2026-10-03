from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService, RAGServiceError

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def ask_question(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    service = RAGService(db=db)

    try:
        return service.answer(question=payload.question, top_k=payload.top_k)
    except RAGServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
