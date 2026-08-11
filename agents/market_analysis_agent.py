import os
from typing import Dict, Any
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/market_analysis_agent.md")
if os.path.exists(PROMPT_PATH):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        MARKET_ANALYSIS_PROMPT = f.read()
else:
    MARKET_ANALYSIS_PROMPT = "You are a Market Intelligence Analyst. Synthesize market viability."


class MarketAnalysisAgent:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GEMINI_API_KEY")
        )
        self.agent = create_deep_agent(
            model=llm,
            tools=[],
            system_prompt=MARKET_ANALYSIS_PROMPT
        )

    def run(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        try:
            startup_idea = shared_memory.get("startup_idea", "")
            search_results = shared_memory.get("search_results", "")

            instruction = (
                f"Perform a market analysis for the startup idea: '{startup_idea}'.\n\n"
                f"Base your analysis on these web search findings:\n{search_results}"
            )

            response = self.agent.invoke({"messages": [("user", instruction)]})
            analysis_output = response["messages"][-1].content

            return {
                "status": "success",
                "data": {
                    "market_summary": analysis_output,
                    "target_idea": startup_idea
                },
                "message": "Market analysis completed successfully."
            }

        except Exception as e:
            return {
                "status": "error",
                "data": {},
                "message": f"MarketAnalysisAgent error: {str(e)}"
            }