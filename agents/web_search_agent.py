import os
from typing import Dict, Any
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.web_search_tool import execute_web_search, WebSearchTool

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/web_search_agent.md")
if os.path.exists(PROMPT_PATH):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        WEB_SEARCH_PROMPT = f.read()
else:
    WEB_SEARCH_PROMPT = "You are a Web Search Agent. Gather facts and competitors for the given startup idea."


class WebSearchAgent:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GEMINI_API_KEY")
        )
        self.agent = create_deep_agent(
            model=llm,
            tools=[execute_web_search],
            system_prompt=WEB_SEARCH_PROMPT
        )
        self.fallback_tool = WebSearchTool()

    def run(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        try:
            startup_idea = shared_memory.get("startup_idea", "")
            if not startup_idea:
                return {
                    "status": "error",
                    "data": {},
                    "message": "Missing 'startup_idea' in state."
                }

            prompt = f"Conduct web search research for the startup idea: '{startup_idea}'"
            response = self.agent.invoke({"messages": [("user", prompt)]})
            
            search_summary = response["messages"][-1].content
            raw_refs = self.fallback_tool.search(startup_idea)
            references = [r["url"] for r in raw_refs if isinstance(r, dict) and "url" in r]

            return {
                "status": "success",
                "data": {
                    "search_results": search_summary,
                    "references": references
                },
                "message": "Web search agent completed successfully."
            }

        except Exception as e:
            return {
                "status": "error",
                "data": {},
                "message": f"WebSearchAgent error: {str(e)}"
            }