import pytest
from unittest.mock import MagicMock
from agents.market_analysis_agent import MarketAnalysisAgent


def test_market_analysis_agent_execution(mocker):
    """Verify MarketAnalysisAgent processes search context correctly."""
    mock_response = {
        "messages": [
            MagicMock(content="Market Analysis: High growth potential with estimated TAM of $1.4B.")
        ]
    }

    agent = MarketAnalysisAgent()
    mocker.patch.object(agent.agent, "invoke", return_value=mock_response)

    sample_state = {
        "startup_idea": "AI legal compliance software",
        "search_results": "Competitors include SixFifty and Vanta."
    }

    result = agent.run(sample_state)

    assert result["status"] == "success"
    assert "market_summary" in result["data"]
    assert "TAM" in result["data"]["market_summary"]