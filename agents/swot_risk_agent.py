"""SWOT & Risk Agent

Evaluates strategic positioning (SWOT) and technical, market, and operational execution risks.
"""
"""
SWOT & Risk Analysis Agent

Input:
    SharedMemory

Output:
{
    "status": "success",
    "data": {
        "strengths": [...],
        "weaknesses": [...],
        "opportunities": [...],
        "threats": [...],
        "risks": [...]
    },
    "message": ""
}
"""

from pathlib import Path


class SWOTRiskAgent:

    def __init__(self):

        prompt_path = Path("prompts/swot_risk_agent.md")

        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            self.system_prompt = ""

    def run(self, shared_memory):

        try:

            startup_idea = shared_memory.get("startup_idea", "")

            market_analysis = shared_memory.get(
                "market_analysis", {}
            )

            competitors = shared_memory.get(
                "competitors", {}
            )

            return {

                "status": "success",

                "data": {

                    "startup_idea": startup_idea,

                    "market_analysis": market_analysis,

                    "competitors": competitors,

                    "system_prompt": self.system_prompt

                },

                "message": "SWOT & Risk Agent completed successfully."

            }

        except Exception as e:

            return {

                "status": "failed",

                "data": None,

                "message": str(e)

            }
