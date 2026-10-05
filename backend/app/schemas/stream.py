"""Typed Server-Sent Events contract for the streaming agent endpoint.

Events expose operational information only: no chain-of-thought, no secrets,
no prompt text. Field values are bounded by the producing service.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

StreamEventType = Literal[
    "message_start",
    "tool_start",
    "tool_result",
    "retrieval",
    "token",
    "message_end",
    "error",
]


class StreamEvent(BaseModel):
    """A single SSE frame.

    ``event`` is the SSE event name; ``data`` holds the safe JSON payload.
    The envelope is intentionally minimal so the wire contract stays stable.
    """

    event: StreamEventType
    data: dict = Field(default_factory=dict)


class MessageStartData(BaseModel):
    request_id: str
    conversation_id: str | None = None


class TokenData(BaseModel):
    text: str = Field(max_length=4000)


class ToolStartData(BaseModel):
    tool: str


class ToolResultData(BaseModel):
    tool: str
    status: Literal["success", "error"]


class RetrievalData(BaseModel):
    count: int = Field(ge=0, le=100)


class MessageEndData(BaseModel):
    answer_kind: str
    tools_used: list[str] = Field(default_factory=list)
    sources: list[dict] = Field(default_factory=list)
    conversation_id: str | None = None


class ErrorData(BaseModel):
    message: str = Field(max_length=500)
    code: str = Field(default="agent_error", max_length=64)
