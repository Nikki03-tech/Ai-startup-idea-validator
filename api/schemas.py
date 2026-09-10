"""Pydantic request/response models for the FastAPI layer."""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ValidateRequest(BaseModel):
    idea: str
    target_audience: str = ""
    industry: str = ""
    constraints: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    # Continue an existing conversation ...
    conversation_id: Optional[int] = None
    # ... or start a new one (session_id is optional grouping metadata,
    # report is required to start a new conversation).
    session_id: Optional[str] = None
    report: Optional[dict[str, Any]] = None

    question: str


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    conversation_id: int
    session_id: Optional[str] = None
    messages: List[MessageOut]
