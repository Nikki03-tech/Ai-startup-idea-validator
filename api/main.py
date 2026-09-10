"""FastAPI API layer for the AI Startup Validator.

Phase 1 only: exposes the existing agent pipeline (Orchestrator) and
Conversational Advisor over HTTP, with PostgreSQL-backed chat history.

This module does NOT duplicate agent/pipeline logic - it calls into
the existing `app.orchestrator.Orchestrator` and
`agents.conversational_advisor.ConversationalAdvisor` exactly as the
Streamlit UI and CLI already do.

Run with:
    uvicorn api.main:app --reload
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from agents.conversational_advisor import ConversationalAdvisor
from api.schemas import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    MessageOut,
    ValidateRequest,
)
from app.orchestrator import Orchestrator
from database.db import engine, get_db, init_db
from database.models import Conversation, Message

# ---------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create chat-history tables on startup if the DB is configured.
    # Do NOT crash app startup if it isn't - /health will just report
    # the DB as unavailable, and /validate (which doesn't need the DB)
    # keeps working.
    if engine is not None:
        init_db()
    yield


app = FastAPI(title="AI Startup Validator API", version="0.1.0", lifespan=lifespan)


# ---------------------------------------------------------------
# Conversational Advisor - built once and reused across requests,
# mirroring the caching the Streamlit UI already does in
# ui/components/advisor_page.py (avoids rebuilding the Gemini/
# DeepAgent client on every chat message).
# ---------------------------------------------------------------

_advisor: Optional[ConversationalAdvisor] = None


def get_advisor() -> ConversationalAdvisor:
    global _advisor
    if _advisor is None:
        _advisor = ConversationalAdvisor()
    return _advisor


# ---------------------------------------------------------------
# Health
# ---------------------------------------------------------------


@app.get("/health")
def health():
    db_status = "not_configured"
    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception as exc:  # pragma: no cover - depends on live DB
            db_status = f"error: {exc}"

    return {"status": "ok", "database": db_status}


# ---------------------------------------------------------------
# Validation endpoint - reuses the existing Orchestrator pipeline
# (the same one app/main.py's CLI and the Streamlit UI drive).
# ---------------------------------------------------------------


@app.post("/validate")
def validate(payload: ValidateRequest):
    orchestrator = Orchestrator()
    orchestrator.receive_request(
        idea=payload.idea,
        target_audience=payload.target_audience,
        industry=payload.industry,
        constraints=payload.constraints,
    )
    orchestrator.execute_pipeline()
    return orchestrator.get_final_output()


# ---------------------------------------------------------------
# Chat endpoint - reuses the existing ConversationalAdvisor. Persists
# every user/assistant turn to PostgreSQL so Phase 2's UI can be
# stateless and just pass conversation_id back and forth.
# ---------------------------------------------------------------


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")

    # -----------------------------------------------------------
    # Existing conversation
    # -----------------------------------------------------------
    if payload.conversation_id is not None:
        conversation = db.get(Conversation, payload.conversation_id)

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="conversation not found",
            )

        # If a validation report is now available, attach it to
        # the existing conversation. This allows a conversation
        # that started before validation to become report-grounded
        # after validation.
        if payload.report:
            conversation.report = payload.report
            db.commit()
            db.refresh(conversation)

        report = conversation.report

    # -----------------------------------------------------------
    # New conversation
    # -----------------------------------------------------------
    else:
        # Report is optional for a new conversation.
        # This allows general chat before validation.
        conversation = Conversation(
            session_id=payload.session_id,
            report=payload.report,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        report = conversation.report

    # Save user message first.
    db.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content=payload.question.strip(),
        )
    )
    db.commit()

    # -----------------------------------------------------------
    # Ask Conversational Advisor
    # -----------------------------------------------------------
    advisor = get_advisor()

    result = advisor.answer_question(
        report,
        payload.question.strip(),
    )

    if result.get("status") != "success":
        raise HTTPException(
            status_code=502,
            detail=result.get("message") or "advisor failed",
        )

    answer = result["answer"]

    # Save assistant response.
    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )
    )
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=answer,
    )

# ---------------------------------------------------------------
# Chat history endpoint
# ---------------------------------------------------------------


@app.get("/chat/history/{conversation_id}", response_model=ChatHistoryResponse)
def chat_history(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")

    return ChatHistoryResponse(
        conversation_id=conversation.id,
        session_id=conversation.session_id,
        messages=[
            MessageOut(role=m.role, content=m.content, created_at=m.created_at)
            for m in conversation.messages
        ],
    )
