"""Tests for the SWOT & Risk Agent."""

import os
import sys
import unittest

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agents.swot_risk_agent import (
    SWOTAnalysis,
    SWOTRiskAgent,
)

class FakeAgent:

    def invoke(self, payload):

        return {
            "structured_response": SWOTAnalysis(
                strengths=[
                    "Large target market"
                ],
                weaknesses=[
                    "High development complexity"
                ],
                opportunities=[
                    "Growing demand"
                ],
                threats=[
                    "Strong competition"
                ],
                risks=[
                    {
                        "risk": "High customer acquisition cost",
                        "severity": "Medium",
                        "mitigation": "Start with a focused niche."
                    }
                ],
            )
        }


class TestSWOTRiskAgent(unittest.TestCase):

    def setUp(self):

        self.agent = SWOTRiskAgent(
            agent=FakeAgent()
        )

    def test_success_response_structure(self):

        shared_memory = {

            "market_analysis": {
                "market_size": "Large",
                "growth": "High",
                "target_audience": "Students",
            },

            "competitors": [
                {
                    "name": "Competitor A",
                    "strengths": ["Strong brand"],
                    "weaknesses": ["Limited personalization"],
                }
            ],
        }

        result = self.agent.run(
            shared_memory
        )

        self.assertEqual(
            result["status"],
            "success"
        )

        self.assertIn(
            "data",
            result
        )

        self.assertIn(
            "swot_analysis",
            result["data"]
        )

        swot = result["data"]["swot_analysis"]

        self.assertIn("strengths", swot)
        self.assertIn("weaknesses", swot)
        self.assertIn("opportunities", swot)
        self.assertIn("threats", swot)
        self.assertIn("risks", swot)

        self.assertGreater(
            len(swot["strengths"]),
            0
        )

        self.assertGreater(
            len(swot["risks"]),
            0
        )

        self.assertEqual(
            swot["risks"][0]["severity"],
            "Medium"
        )

        self.assertIn(
            "mitigation",
            swot["risks"][0]
        )

        self.assertEqual(
            result["message"],
            ""
        )


if __name__ == "__main__":
    unittest.main()