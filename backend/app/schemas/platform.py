from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse


class AgentChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    conversation_id: UUID | None = None


class AgentEvent(BaseModel):
    event: str
    tool: str | None = None
    detail: str | None = None


class AgentSource(BaseModel):
    document_id: UUID
    filename: str
    chunk_id: UUID
    chunk_index: int
    similarity: float


class AgentChatResponse(BaseModel):
    answer: str
    answer_kind: str
    sources: list[AgentSource] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    events: list[AgentEvent] = Field(default_factory=list)
    conversation_id: UUID | None = None


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=200)


class ConversationMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)
