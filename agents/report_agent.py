"""
Report Generation Agent
"""

from pathlib import Path


class ReportAgent:

    def __init__(self):

        prompt_path = Path("prompts/report_agent.md")

        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(
                encoding="utf-8"
            )
        else:
            self.system_prompt = ""

    def run(self, shared_memory):

        try:

            report = {
                "startup_idea": shared_memory.get("startup_idea", ""),
                "idea_extraction": shared_memory.get("idea_extraction", {}),
                "web_search_results": shared_memory.get("web_search_results", {}),
                "market_analysis": shared_memory.get("market_analysis", {}),
                "competitor_analysis": shared_memory.get("competitor_analysis", {}),
                "swot_analysis": shared_memory.get("swot_analysis", {}),
                "mvp_recommendation": shared_memory.get("mvp_recommendation", {}),
                "gtm_strategy": shared_memory.get("gtm_strategy", {}),
                "system_prompt": self.system_prompt,
            }

            return {
                "status": "success",
                "data": report,
                "message": "Report generated successfully."
            }

        except Exception as e:

            return {
                "status": "failed",
                "data": None,
                "message": str(e)
            }