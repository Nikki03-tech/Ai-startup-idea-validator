import pytest
from unittest.mock import MagicMock
from agents.web_search_agent import WebSearchAgent


def test_web_search_agent_missing_input():
    agent = WebSearchAgent()
    result = agent.run({})
    assert result["status"] == "error"
    assert "Missing 'startup_idea'" in result["message"]


def test_web_search_agent_execution(mocker):
    # Mock LLM invoke call
    mock_llm_response = {
        "messages": [
            MagicMock(content="Found market trends for AI e-commerce agents.")
        ]
    }
    
    # Mock DuckDuckGo fallback tool search response
    mock_search_results = [
        {"title": "Competitor 1", "url": "https://example.com/1"},
        {"title": "Competitor 2", "url": "https://example.com/2"}
    ]

    agent = WebSearchAgent()
    
    # Patch the agent's internal invocation and search method
    mocker.patch.object(agent.agent, "invoke", return_value=mock_llm_response)
    mocker.patch.object(agent.fallback_tool, "search", return_value=mock_search_results)

    state = {"startup_idea": "AI customer support agent for e-commerce"}
    result = agent.run(state)

    assert result["status"] == "success"
    assert "search_results" in result["data"]
    assert "references" in result["data"]
    assert len(result["data"]["references"]) == 2