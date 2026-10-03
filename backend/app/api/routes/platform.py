from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.conversation import Conversation, Message
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.schemas.platform import (
    AgentChatRequest,
    AgentChatResponse,
    ConversationCreateRequest,
    ConversationMessageRequest,
    ConversationResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    SessionResponse,
    UserResponse,
)
from app.services.agent_provider import DecisionRequest, FakeDecisionProvider, OpenAIDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.auth_service import current_user, login_user, logout_user, register_user
from app.services.ingestion_service import DocumentIngestionService, IngestionError
from app.services.retrieval_service import RetrievalService
from app.services.tool_registry import ToolRegistry

router = APIRouter(tags=["identity", "conversations", "agent"])


def _service(db: Session) -> AgentOrchestrationService:
    retrieval = RetrievalService(db)
    settings = __import__("app.core.settings", fromlist=["get_settings"]).get_settings()
    provider = (
        OpenAIDecisionProvider(settings.openai_api_key, settings.llm_model)
        if settings.llm_provider.lower() == "openai" and settings.openai_api_key
        else FakeDecisionProvider()
    )
    return AgentOrchestrationService(provider, ToolRegistry(retrieval))


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    user = register_user(db, payload)
    return UserResponse(id=user.id, email=user.email)


@router.post("/auth/login", response_model=SessionResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> SessionResponse:
    user, token, expires = login_user(db, payload)
    return SessionResponse(access_token=token, expires_at=expires, user=UserResponse(id=user.id, email=user.email))


@router.post("/auth/logout", status_code=204)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(__import__("fastapi.security", fromlist=["HTTPBearer"]).HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Response:
    logout_user(db, credentials)
    return Response(status_code=204)


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
def create_conversation(
    payload: ConversationCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ConversationResponse:
    conversation = Conversation(user_id=user.id, title=payload.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ConversationResponse(id=conversation.id, title=conversation.title, created_at=conversation.created_at, updated_at=conversation.updated_at, messages=[])


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ConversationResponse]:
    rows = db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc())).all()
    return [ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=[]) for c in rows]


def _owned_conversation(db: Session, user: User, conversation_id) -> Conversation:
    row = db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return row


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    c = _owned_conversation(db, user, conversation_id)
    messages = [MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in c.messages]
    return ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=messages)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Response:
    c = _owned_conversation(db, user, conversation_id)
    db.delete(c)
    db.commit()
    return Response(status_code=204)


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
def add_message(conversation_id, payload: ConversationMessageRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    c = _owned_conversation(db, user, conversation_id)
    context_rows = db.scalars(select(Message).where(Message.conversation_id == c.id).order_by(Message.created_at.desc()).limit(20)).all()
    context_rows = list(reversed(context_rows))
    db.add(Message(conversation_id=c.id, role="user", content=payload.content))
    db.flush()

    context = "\n".join(f"{m.role}: {m.content[:1000]}" for m in context_rows)[-8000:]
    result = _service(db).run(payload.content, context=context, user_id=user.id)
    db.add(Message(conversation_id=c.id, role="assistant", content=result.answer, metadata_json={"answer_kind": result.answer_kind, "tools_used": result.tools_used, "sources": [s.model_dump(mode="json") for s in result.sources]}))
    db.commit()
    db.refresh(c)
    messages = [MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in c.messages]
    return ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=messages)


@router.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat(payload: AgentChatRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AgentChatResponse:
    context = ""
    conversation_id = payload.conversation_id
    if conversation_id:
        conversation = _owned_conversation(db, user, conversation_id)
        recent = db.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(20)).all()
        context = "\n".join(f"{m.role}: {m.content[:1000]}" for m in reversed(recent))[-8000:]
        db.add(Message(conversation_id=conversation.id, role="user", content=payload.question))
        db.flush()

    result = _service(db).run(payload.question, context=context, user_id=user.id)
    if conversation_id:
        db.add(Message(conversation_id=conversation_id, role="assistant", content=result.answer, metadata_json={"answer_kind": result.answer_kind, "tools_used": result.tools_used, "sources": [s.model_dump(mode="json") for s in result.sources]}))
        db.commit()
    return result


@router.post("/me/documents", response_model=list[dict])
def own_documents(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    docs = db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())).all()
    return [{"id": d.id, "filename": d.filename, "content_type": d.content_type, "status": d.status, "chunk_count": len(d.chunks), "created_at": d.created_at} for d in docs]


@router.post("/me/documents/upload", status_code=201)
def upload_owned_document(file: __import__("fastapi").UploadFile = __import__("fastapi").File(...), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    try:
        document, count = DocumentIngestionService(db).ingest(file, user_id=user.id)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": document.id, "filename": document.filename, "chunk_count": count}
