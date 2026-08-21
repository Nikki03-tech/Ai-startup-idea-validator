"""Tests for the Competitor Agent."""

import os
import sys
import unittest

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agents.competitor_agent import (
    CompetitorAnalysis,
    CompetitorAgent,
)


class FakeAgent:

    def invoke(self, payload):

        # Sanity check: the prior web search context should be threaded
        # into the instruction (Phase 5 fix - avoid duplicate research).
        content = payload["messages"][0][1]
        assert "MealMate" in content

        return {
            "structured_response": CompetitorAnalysis(
                competitors=[
                    {
                        "name": "Competitor A",
                        "website": "https://competitor-a.example.com",
                        "description": "An existing meal-planning app.",
                        "strengths": ["Large user base"],
                        "weaknesses": ["No dietary-restriction support"],
                        "source_urls": ["https://example.com/article"],
                    }
                ]
            )
        }


class TestCompetitorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = CompetitorAgent(agent=FakeAgent())

    def test_success_response_structure(self):
        shared_memory = {
            "startup_idea": "AI-powered meal planning app for people with dietary restrictions",
            "search_results": "Existing apps include MealMate and PlanEat.",
            "references": ["https://example.com/article"],
        }

        result = self.agent.run(shared_memory)

        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("competitors", result["data"])

        competitors = result["data"]["competitors"]
        self.assertEqual(len(competitors), 1)
        self.assertEqual(competitors[0]["name"], "Competitor A")
        self.assertIn("strengths", competitors[0])
        self.assertIn("weaknesses", competitors[0])

    def test_missing_startup_idea_returns_error(self):
        result = self.agent.run({})

        self.assertEqual(result["status"], "error")
        self.assertIn("Missing 'startup_idea'", result["message"])


if __name__ == "__main__":
    unittest.main()
