from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.dependencies import get_db
from app.models.conversation import Conversation, Message
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
from app.services.agent_provider import FakeDecisionProvider, OpenAIDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.auth_service import current_user, login_user, logout_user, register_user
from app.services.retrieval_service import RetrievalService
from app.services.tool_registry import ToolRegistry

router = APIRouter(tags=["identity", "conversations", "agent"])


def _service(db: Session) -> AgentOrchestrationService:
    retrieval = RetrievalService(db)
    settings = get_settings()
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        provider = OpenAIDecisionProvider(settings.openai_api_key, settings.llm_model)
    else:
        provider = FakeDecisionProvider()
    return AgentOrchestrationService(provider, ToolRegistry(retrieval))


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    user = register_user(db, payload)
    return UserResponse(id=user.id, email=user.email)


@router.post("/auth/login", response_model=SessionResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> SessionResponse:
    user, token, expires = login_user(db, payload)
    return SessionResponse(access_token=token, expires_at=expires, user=UserResponse(id=user.id, email=user.email))


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: Session = Depends(get_db), user: User = Depends(current_user)) -> Response:
    logout_user(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreateRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    c = Conversation(user_id=user.id, title=payload.title)
    db.add(c)
    db.commit()
    db.refresh(c)
    return ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=[])


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ConversationResponse]:
    rows = db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc())).all()
    return [ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=[]) for c in rows]


def _owned_conversation(db: Session, user: User, conversation_id) -> Conversation:
    row = db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return row


def _messages_response(c: Conversation) -> list[MessageResponse]:
    return [MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in c.messages]


def _memory_context(db: Session, c: Conversation) -> str:
    settings = get_settings()
    recent = db.scalars(select(Message).where(Message.conversation_id == c.id).order_by(Message.created_at.desc()).limit(settings.max_conversation_messages)).all()
    return "\n".join(f"{m.role}: {m.content[:1200]}" for m in reversed(recent))[-settings.max_conversation_context_chars:]


def _store_result(db: Session, c: Conversation, question: str, result: AgentChatResponse) -> None:
    db.add(Message(conversation_id=c.id, role="user", content=question))
    db.add(Message(conversation_id=c.id, role="assistant", content=result.answer, metadata_json={"answer_kind": result.answer_kind, "tools_used": result.tools_used, "sources": [s.model_dump(mode="json") for s in result.sources], "events": [e.model_dump() for e in result.events]}))
    c.updated_at = datetime.now(timezone.utc)
    db.commit()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    c = _owned_conversation(db, user, conversation_id)
    return ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=_messages_response(c))


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Response:
    c = _owned_conversation(db, user, conversation_id)
    db.delete(c)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
def add_message(conversation_id, payload: ConversationMessageRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    c = _owned_conversation(db, user, conversation_id)
    context = _memory_context(db, c)
    result = _service(db).run(payload.content, context=context, user_id=user.id).response()
    _store_result(db, c, payload.content, result)
    db.refresh(c)
    return ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=_messages_response(c))


@router.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat(payload: AgentChatRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AgentChatResponse:
    context = ""
    c = None
    if payload.conversation_id is not None:
        c = _owned_conversation(db, user, payload.conversation_id)
        context = _memory_context(db, c)
    result = _service(db).run(payload.question, context=context, user_id=user.id).response()
    if c is not None:
        _store_result(db, c, payload.question, result)
        result.conversation_id = c.id
    return result
