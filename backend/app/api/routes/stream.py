from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rate_limit import RateLimitExceeded, ai_request_limiter
from app.core.settings import get_settings
from app.core.telemetry import record, reset_request_id, set_request_id
from app.db.session import SessionLocal
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.platform import AgentChatRequest
from app.schemas.stream import StreamEvent
from app.services.agent_provider import FakeDecisionProvider, OpenAIDecisionProvider
from app.services.auth_service import current_user
from app.services.retrieval_service import SessionScopedRetrieval
from app.services.stream_agent_service import StreamAgentService
from app.services.tool_registry import ToolRegistry

router = APIRouter(tags=["agent", "streaming"])


def _stream_service() -> StreamAgentService:
    settings = get_settings()
    retrieval = SessionScopedRetrieval(SessionLocal)
    provider = (
        OpenAIDecisionProvider(settings.openai_api_key, settings.llm_model)
        if settings.llm_provider.lower() == "openai" and settings.openai_api_key
        else FakeDecisionProvider()
    )
    return StreamAgentService(provider, ToolRegistry(retrieval))


def _owned_conversation(db: Session, user_id: UUID, conversation_id: UUID) -> Conversation:
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def _memory_context(db: Session, conversation: Conversation) -> str:
    settings = get_settings()
    recent = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(settings.max_conversation_messages)
    ).all()
    return "\n".join(
        f"{message.role}: {message.content[:1200]}" for message in reversed(recent)
    )[-settings.max_conversation_context_chars:]


def _persist_exchange(
    conversation_id: UUID,
    user_id: UUID,
    question: str,
    answer: str,
    answer_kind: str,
    tools_used: list[str],
    sources: list[dict],
) -> None:
    with SessionLocal() as db:
        conversation = _owned_conversation(db, user_id, conversation_id)
        db.add_all(
            [
                Message(conversation_id=conversation.id, role="user", content=question),
                Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=answer,
                    metadata_json={
                        "answer_kind": answer_kind,
                        "tools_used": tools_used,
                        "sources": sources,
                        "events": [{"event": "streamed"}],
                    },
                ),
            ]
        )
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()


@router.post("/agent/chat/stream")
async def agent_chat_stream(
    payload: AgentChatRequest,
    request: Request,
    user: User = Depends(current_user),
):
    settings = get_settings()
    if len(payload.question) > settings.max_prompt_chars:
        raise HTTPException(status_code=413, detail="Prompt exceeds maximum allowed size")
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.max_request_body_bytes:
                raise HTTPException(status_code=413, detail="Request body exceeds maximum allowed size")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length") from exc
    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        raise RuntimeError("Canonical request ID middleware is not installed")
    try:
        ai_request_limiter.check(str(user.id))
    except RateLimitExceeded as exc:
        record("rate_limit", category="ai")
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    conversation_id = payload.conversation_id
    context = ""
    if conversation_id is not None:
        with SessionLocal() as db:
            conversation = _owned_conversation(db, user.id, conversation_id)
            context = _memory_context(db, conversation)

    service = _stream_service()
    started = time.monotonic()

    async def event_generator():
        token = set_request_id(request_id)
        completed = False
        output: list[str] = []
        terminal = False
        stream = service.stream(payload.question, context=context, user_id=user.id)
        try:
            yield _sse(
                "message_start",
                {"request_id": request_id, "conversation_id": str(conversation_id) if conversation_id else None},
            )
            for name, data in stream:
                if await request.is_disconnected():
                    record("stream_disconnect", request_id=request_id)
                    break
                if name == "token":
                    output.append(data["text"])
                elif name == "message_end":
                    completed = True
                if name in {"message_end", "error"}:
                    if terminal:
                        break
                    terminal = True
                yield _sse(name, data)
                if terminal:
                    if completed and conversation_id is not None and not await request.is_disconnected():
                        try:
                            _persist_exchange(
                                conversation_id,
                                user.id,
                                payload.question,
                                "".join(output),
                                data["answer_kind"],
                                data["tools_used"],
                                data["sources"],
                            )
                        except Exception:
                            record("stream_persist_failure", request_id=request_id, error_category="storage")
                    break
            record(
                "agent_stream_complete",
                request_id=request_id,
                terminal=terminal,
                success=completed,
                duration_ms=round((time.monotonic() - started) * 1000, 3),
            )
        except asyncio.CancelledError:
            record(
                "agent_stream_cancelled",
                request_id=request_id,
                terminal=False,
                success=False,
                error_category="cancelled",
            )
            raise
        finally:
            stream.close()
            reset_request_id(token)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-store",
            "X-Accel-Buffering": "no",
            "X-Request-Id": request_id,
        },
    )


def _sse(event: str, data: dict) -> str:
    typed = StreamEvent(event=event, data=data)
    return f"event: {typed.event}\ndata: {json.dumps(typed.data, separators=(',', ':'))}\n\n"
