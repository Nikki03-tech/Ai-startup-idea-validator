"""MVP Recommendation Agent

Generates prioritized MVP features, core user journeys, and development launch roadmap.
"""
"""
MVP Recommendation Agent

Input:
    SharedMemory

Output:
{
    "status":"success",
    "data":{
        "must_have":[...],
        "nice_to_have":[...],
        "future_features":[...]
    },
    "message":""
}
"""
from pathlib import Path


class MVPRecommendationAgent:

    def __init__(self):

        prompt_path = Path("prompts/mvp_agent.md")

        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(
                encoding="utf-8"
            )
        else:
            self.system_prompt = ""

    def run(self, shared_memory):

        try:

            swot_analysis = shared_memory.get(
                "swot_analysis",
                {}
            )

            mvp_recommendation = {

                "swot_analysis": swot_analysis,

                "system_prompt": self.system_prompt

            }

            return {

                "status": "success",

                "data": {

                    "mvp_recommendation": mvp_recommendation

                },

                "message": "MVP Recommendation completed successfully."

            }

        except Exception as e:

            return {

                "status": "failed",

                "data": None,

                "message": str(e)

            }