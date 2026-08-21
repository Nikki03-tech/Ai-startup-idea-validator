import pytest
from unittest.mock import MagicMock
from langchain_core.messages import ToolMessage
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


def test_web_search_agent_uses_real_tool_output_not_filler_status(mocker):
    """
    Regression test: when the deep agent DID call execute_web_search
    (a real ToolMessage is present) but its own final AI message is
    just a generic status update ("research is underway"), the agent
    must report the actual tool findings, not the filler text.
    """

    tool_message = ToolMessage(
        content="AI meal-planning apps market: key players include Mealime and PlateJoy.",
        tool_call_id="call_1",
    )
    final_ai_message = MagicMock(content="Research is underway.")

    mock_llm_response = {"messages": [tool_message, final_ai_message]}

    agent = WebSearchAgent()
    mocker.patch.object(agent.agent, "invoke", return_value=mock_llm_response)
    mocker.patch.object(agent.fallback_tool, "search")

    state = {"startup_idea": "AI meal planning app"}
    result = agent.run(state)

    assert result["status"] == "success"
    search_results = result["data"]["search_results"]

    assert "Mealime" in search_results
    assert "PlateJoy" in search_results
    # The fallback should NOT have been called - a real tool call
    # already happened.
    agent.fallback_tool.search.assert_not_called()
