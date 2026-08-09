"""Tests for the MVP Recommendation Agent."""

import os
import sys
import unittest

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agents.mvp_recommendation_agent import (
    MVPRecommendation,
    MVPRecommendationAgent,
)

class FakeAgent:

    def invoke(self, payload):

        return {
            "structured_response": MVPRecommendation(
                must_have=[
                    {
                        "feature": "Core AI recommendation",
                        "reason": "This is the core value proposition.",
                        "validation_goal": (
                            "Test whether users find the "
                            "recommendations useful."
                        ),
                    }
                ],
                nice_to_have=[
                    {
                        "feature": "Notifications",
                        "reason": "Useful for engagement but not essential.",
                        "validation_goal": (
                            "Test whether reminders improve retention."
                        ),
                    }
                ],
                future_features=[
                    {
                        "feature": "Community platform",
                        "reason": "Not required to validate the core idea.",
                        "validation_goal": (
                            "Test community demand after initial validation."
                        ),
                    }
                ],
                prioritization_rationale=(
                    "The MVP focuses on the core value proposition "
                    "before adding secondary functionality."
                ),
            )
        }


class TestMVPRecommendationAgent(unittest.TestCase):

    def setUp(self):

        self.agent = MVPRecommendationAgent(
            agent=FakeAgent()
        )

    def test_success_response_structure(self):

        shared_memory = {

            "swot_analysis": {

                "strengths": [
                    "Strong market demand"
                ],

                "weaknesses": [
                    "High competition"
                ],

                "opportunities": [
                    "Growing customer interest"
                ],

                "threats": [
                    "Established competitors"
                ],

                "risks": [
                    {
                        "risk": "Customer acquisition cost",
                        "severity": "Medium",
                        "mitigation": "Start with a niche."
                    }
                ],
            }
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
            "mvp_recommendation",
            result["data"]
        )

        mvp = result["data"]["mvp_recommendation"]

        self.assertIn(
            "must_have",
            mvp
        )

        self.assertIn(
            "nice_to_have",
            mvp
        )

        self.assertIn(
            "future_features",
            mvp
        )

        self.assertIn(
            "prioritization_rationale",
            mvp
        )

        self.assertGreater(
            len(mvp["must_have"]),
            0
        )

        self.assertIn(
            "feature",
            mvp["must_have"][0]
        )

        self.assertIn(
            "reason",
            mvp["must_have"][0]
        )

        self.assertIn(
            "validation_goal",
            mvp["must_have"][0]
        )

        self.assertEqual(
            result["message"],
            ""
        )


if __name__ == "__main__":
    unittest.main()