"""
Go-To-Market Strategy Agent
"""

from pathlib import Path


class GTMStrategyAgent:

    def __init__(self):

        prompt_path = Path("prompts/gtm_agent.md")

        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(
                encoding="utf-8"
            )
        else:
            self.system_prompt = ""

    def run(self, shared_memory):

        try:

            startup_idea = shared_memory.get("startup_idea", "")
            market_analysis = shared_memory.get("market_analysis", {})
            mvp_recommendation = shared_memory.get("mvp_recommendation", {})

            gtm_strategy = {
                "startup_idea": startup_idea,
                "market_analysis": market_analysis,
                "mvp_recommendation": mvp_recommendation,
                "system_prompt": self.system_prompt,
            }

            return {
                "status": "success",
                "data": {
                    "gtm_strategy": gtm_strategy
                },
                "message": "Go-To-Market Strategy generated successfully."
            }

        except Exception as e:

            return {
                "status": "failed",
                "data": None,
                "message": str(e)
            }