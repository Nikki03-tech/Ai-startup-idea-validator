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
            self.system_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            self.system_prompt = ""

    def run(self, shared_memory):

        try:

            startup_idea = shared_memory.get("startup_idea", "")

            return {

                "status": "success",

                "data": {

                    "startup_idea": startup_idea,

                    "system_prompt": self.system_prompt

                },

                "message": "MVP Recommendation completed successfully."

            }

        except Exception as e:

            return {

                "status": "failed",

                "data": None,

                "message": str(e)

            }
