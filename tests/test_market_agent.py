"""Tests for the Market Analysis Agent."""

import os
import sys
import unittest

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agents.market_analysis_agent import (
    MarketAnalysis,
    MarketAnalysisAgent,
)


class FakeAgent:

    def invoke(self, payload):

        return {
            "structured_response": MarketAnalysis(
                market_size="Estimated $1.4B addressable market based on search findings.",
                target_audience="Early-stage founders and small legal teams.",
                industry_trends="Growing adoption of AI compliance tooling.",
                opportunities="Gap in affordable compliance automation for startups.",
                market_potential="High, contingent on differentiated pricing.",
            )
        }


class TestMarketAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.agent = MarketAnalysisAgent(agent=FakeAgent())

    def test_success_response_structure(self):
        shared_memory = {
            "startup_idea": "AI legal compliance software",
            "search_results": "Competitors include SixFifty and Vanta.",
        }

        result = self.agent.run(shared_memory)

        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("market_analysis", result["data"])

        market_analysis = result["data"]["market_analysis"]

        self.assertIn("market_size", market_analysis)
        self.assertIn("target_audience", market_analysis)
        self.assertIn("industry_trends", market_analysis)
        self.assertIn("opportunities", market_analysis)
        self.assertIn("market_potential", market_analysis)

        self.assertIn("$1.4B", market_analysis["market_size"])

    def test_missing_startup_idea_returns_error(self):
        result = self.agent.run({"search_results": "some findings"})

        self.assertEqual(result["status"], "error")
        self.assertIn("startup_idea", result["message"])


if __name__ == "__main__":
    unittest.main()
