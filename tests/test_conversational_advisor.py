import pytest
from unittest.mock import MagicMock
from agents.conversational_advisor import ConversationalAdvisor


def test_advisor_answers_using_report(mocker):
    """Verify ConversationalAdvisor answers a question using the supplied report."""
    mock_response = {
        "messages": [
            MagicMock(content="Your top competitor is Acme Corp, based on the report.")
        ]
    }

    agent = ConversationalAdvisor(agent=MagicMock())
    mocker.patch.object(agent.agent, "invoke", return_value=mock_response)

    report = {
        "executive_summary": "Promising idea with moderate competition.",
        "competitor_analysis": [{"name": "Acme Corp"}],
    }

    result = agent.answer_question(report, "Who is my biggest competitor?")

    assert result["status"] == "success"
    assert "Acme Corp" in result["answer"]


def test_advisor_rejects_empty_report():
    """Verify ConversationalAdvisor fails gracefully when no report is supplied."""
    agent = ConversationalAdvisor(agent=MagicMock())

    result = agent.answer_question({}, "What is the market size?")

    assert result["status"] == "failed"
    assert "report" in result["message"].lower()


def test_advisor_rejects_empty_question():
    """Verify ConversationalAdvisor fails gracefully when no question is supplied."""
    agent = ConversationalAdvisor(agent=MagicMock())

    result = agent.answer_question({"executive_summary": "ok"}, "   ")

    assert result["status"] == "failed"
    assert "question" in result["message"].lower()
