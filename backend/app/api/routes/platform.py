from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rate_limit import RateLimitExceeded, ai_request_limiter
from app.core.settings import get_settings
from app.core.telemetry import record
from app.db.dependencies import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.platform import (
    AgentChatRequest, AgentChatResponse, ConversationCreateRequest,
    ConversationMessageRequest, ConversationResponse, LoginRequest,
    MessageResponse, RegisterRequest, SessionResponse, UserResponse,
)
from app.services.agent_provider import FakeDecisionProvider, OpenAIDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.auth_service import current_user, login_user, logout_user, register_user
from app.services.retrieval_service import RetrievalService
from app.services.tool_registry import ToolRegistry

router = APIRouter(tags=["identity", "conversations", "agent"])


def _check_ai_limit(user: User) -> None:
    try:
        ai_request_limiter.check(str(user.id))
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc


def _service(db: Session) -> AgentOrchestrationService:
    retrieval = RetrievalService(db)
    settings = get_settings()
    provider = (
        OpenAIDecisionProvider(settings.openai_api_key, settings.llm_model)
        if settings.llm_provider.lower() == "openai" and settings.openai_api_key
        else FakeDecisionProvider()
    )
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
    conversation = Conversation(user_id=user.id, title=payload.title)
    db.add(conversation); db.commit(); db.refresh(conversation)
    return ConversationResponse(id=conversation.id, title=conversation.title, created_at=conversation.created_at, updated_at=conversation.updated_at, messages=[])


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ConversationResponse]:
    rows = db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc())).all()
    return [ConversationResponse(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at, messages=[]) for c in rows]


def _owned_conversation(db: Session, user: User, conversation_id: UUID) -> Conversation:
    conversation = db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


def _memory_context(db: Session, conversation: Conversation) -> str:
    settings = get_settings()
    recent = db.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc(), Message.id.desc()).limit(settings.max_conversation_messages)).all()
    return "\n".join(f"{message.role}: {message.content[:1200]}" for message in reversed(recent))[-settings.max_conversation_context_chars:]


def _persist_exchange(db: Session, conversation: Conversation, question: str, result: AgentChatResponse) -> None:
    db.add_all([
        Message(conversation_id=conversation.id, role="user", content=question),
        Message(conversation_id=conversation.id, role="assistant", content=result.answer,
                metadata_json={"answer_kind": result.answer_kind, "tools_used": result.tools_used,
                               "sources": [source.model_dump(mode="json") for source in result.sources],
                               "events": [event.model_dump() for event in result.events]}),
    ])
    conversation.updated_at = datetime.now(timezone.utc); db.commit()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    conversation = _owned_conversation(db, user, conversation_id)
    messages = [MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in conversation.messages]
    return ConversationResponse(id=conversation.id, title=conversation.title, created_at=conversation.created_at, updated_at=conversation.updated_at, messages=messages)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: UUID, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Response:
    conversation = _owned_conversation(db, user, conversation_id); db.delete(conversation); db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
def add_message(conversation_id: UUID, payload: ConversationMessageRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ConversationResponse:
    _check_ai_limit(user)
    settings = get_settings()
    if len(payload.content) > settings.max_prompt_chars:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Prompt exceeds maximum allowed size")
    conversation = _owned_conversation(db, user, conversation_id)
    context = _memory_context(db, conversation)
    result = _service(db).run(payload.content, context=context, user_id=user.id).response()
    _persist_exchange(db, conversation, payload.content, result); db.refresh(conversation)
    messages = [MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in conversation.messages]
    return ConversationResponse(id=conversation.id, title=conversation.title, created_at=conversation.created_at, updated_at=conversation.updated_at, messages=messages)


@router.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat(payload: AgentChatRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AgentChatResponse:
    settings = get_settings()
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.max_request_body_bytes:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Request body exceeds maximum allowed size")
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Content-Length") from exc
    _check_ai_limit(user)
    if len(payload.question) > settings.max_prompt_chars:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Prompt exceeds maximum allowed size")
    conversation = _owned_conversation(db, user, payload.conversation_id) if payload.conversation_id is not None else None
    context = _memory_context(db, conversation) if conversation is not None else ""
    result = _service(db).run(payload.question, context=context, user_id=user.id).response()
    if conversation is not None:
        _persist_exchange(db, conversation, payload.question, result); result.conversation_id = conversation.id
    record("agent_chat_complete", endpoint="/agent/chat", success=result.answer_kind != "INSUFFICIENT_EVIDENCE")
    return result
