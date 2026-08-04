"""Tests for SWOT & Risk Agent."""
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agents.swot_risk_agent import SWOTRiskAgent


class TestSWOTRiskAgent(unittest.TestCase):

    def setUp(self):
        self.agent = SWOTRiskAgent()

    def test_success_response_structure(self):

        shared_memory = {

            "market_analysis": {
                "market_size": "Large",
                "growth": "High"
            },

            "competitors": [
                "Competitor A",
                "Competitor B"
            ]

        }

        result = self.agent.run(shared_memory)

        self.assertEqual(result["status"], "success")

        self.assertIn("data", result)

        self.assertIn("swot_analysis", result["data"])

        self.assertIn("message", result)


if __name__ == "__main__":
    unittest.main()
