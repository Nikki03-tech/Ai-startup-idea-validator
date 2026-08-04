"""Tests for MVP Recommendation Agent."""
import unittest

from agents.mvp_recommendation_agent import MVPRecommendationAgent


class TestMVPRecommendationAgent(unittest.TestCase):

    def setUp(self):
        self.agent = MVPRecommendationAgent()

    def test_success_response_structure(self):

        shared_memory = {

            "swot_analysis": {

                "strengths": [
                    "Growing market"
                ],

                "weaknesses": [
                    "New company"
                ]
            }

        }

        result = self.agent.run(shared_memory)

        self.assertEqual(result["status"], "success")

        self.assertIn("data", result)

        self.assertIn("mvp_recommendation", result["data"])

        self.assertIn("message", result)


if __name__ == "__main__":
    unittest.main()
