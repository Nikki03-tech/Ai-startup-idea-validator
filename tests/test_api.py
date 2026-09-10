"""Essential tests for the Phase 1 FastAPI layer.

Scope (per Phase 1 instructions - no large test framework):
- API starts and /health responds.
- /validate calls into the existing Orchestrator (mocked - no live
  Gemini calls).
- /chat stores + returns messages, and /chat/history retrieves them,
  against a real SQLAlchemy-backed database (SQLite in-memory here,
  since no live PostgreSQL server is available in this environment -
  see the run notes for what still needs verifying against real
  Postgres).
- ConversationalAdvisor.answer_question is mocked so no live Gemini
  call is made.
"""

import os
import sys
from unittest import mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Dummy key so importing agents/orchestrator code (which builds real
# clients at construction time) doesn't fail - no network call is made
# because Orchestrator/ConversationalAdvisor are mocked below.
os.environ.setdefault("GEMINI_API_KEY", "dummy_key_for_tests")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.db import Base


@pytest.fixture()
def client():
    """A TestClient wired to an isolated in-memory SQLite database.

    Uses the same SQLAlchemy models as production (database/models.py)
    so the store/retrieve logic in api/main.py is exercised for real -
    only the underlying database engine differs from a deployed
    PostgreSQL instance.
    """

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    from api.main import app
    from database.db import get_db

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validate_calls_orchestrator(client):
    fake_output = {"startup_idea": {"idea": "test idea"}, "execution_plan": []}

    with mock.patch("api.main.Orchestrator") as MockOrchestrator:
        instance = MockOrchestrator.return_value
        instance.get_final_output.return_value = fake_output

        response = client.post("/validate", json={"idea": "test idea"})

    assert response.status_code == 200
    assert response.json() == fake_output
    instance.receive_request.assert_called_once()
    instance.execute_pipeline.assert_called_once()


def test_chat_requires_report_for_new_conversation(client):
    response = client.post("/chat", json={"question": "How big is the market?"})
    assert response.status_code == 400


def test_chat_and_history_roundtrip(client):
    fake_report = {"executive_summary": "Looks promising."}

    with mock.patch("api.main.get_advisor") as mock_get_advisor:
        mock_advisor = mock_get_advisor.return_value
        mock_advisor.answer_question.return_value = {
            "status": "success",
            "answer": "The market looks strong based on the report.",
            "message": "",
        }

        first = client.post(
            "/chat",
            json={
                "question": "How big is the market?",
                "report": fake_report,
                "session_id": "session-123",
            },
        )
        assert first.status_code == 200
        body = first.json()
        conversation_id = body["conversation_id"]
        assert body["answer"] == "The market looks strong based on the report."

        # Follow-up question reuses the stored report - no need to
        # resend it.
        second = client.post(
            "/chat",
            json={"conversation_id": conversation_id, "question": "And competitors?"},
        )
        assert second.status_code == 200
        assert mock_advisor.answer_question.call_count == 2

    history = client.get(f"/chat/history/{conversation_id}")
    assert history.status_code == 200
    messages = history.json()["messages"]

    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    assert messages[0]["content"] == "How big is the market?"
    assert messages[1]["content"] == "The market looks strong based on the report."


def test_chat_history_missing_conversation_returns_404(client):
    response = client.get("/chat/history/999999")
    assert response.status_code == 404
