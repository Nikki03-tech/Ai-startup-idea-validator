"""Competitor Agent

Discovers, analyzes, and compares direct & indirect competitors using a
DeepAgent with live web search and structured output.

Input:
    SharedMemory (expects "startup_idea")

Output:
{
    "status": "success",
    "data": {
        "startup_idea": "...",
        "competitors": [
            {
                "name": "...",
                "website": "...",
                "description": "...",
                "strengths": [...],
                "weaknesses": [...],
                "source_urls": [...]
            }
        ]
    },
    "message": ""
}
"""

import os
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv

load_dotenv()

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from tools.web_search_tool import execute_web_search
from state.schema import Competitor

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/competitor_agent.md")
if os.path.exists(PROMPT_PATH):
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        COMPETITOR_AGENT_PROMPT = f.read()
else:
    COMPETITOR_AGENT_PROMPT = (
        "You are a Competitor Analysis Agent. Search the web to find real "
        "competitors for the given startup idea."
    )


class CompetitorAnalysis(BaseModel):
    """Structured competitor analysis output."""

    competitors: List[Competitor] = Field(
        description="Real competitors found via web search, with strengths and weaknesses."
    )


class CompetitorAgent:

    def __init__(self, model_name: str = "gemini-3.6-flash"):
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GEMINI_API_KEY")
        )
        self.agent = create_deep_agent(
            model=llm,
            tools=[execute_web_search],
            system_prompt=COMPETITOR_AGENT_PROMPT,
            response_format=CompetitorAnalysis,
        )

    def run(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:

        try:
            startup_idea = shared_memory.get("startup_idea", "")

            if not startup_idea:
                return {
                    "status": "error",
                    "data": {},
                    "message": "Missing 'startup_idea' in state."
                }

            instruction = (
                f"Find real competitors for this startup idea: '{startup_idea}'.\n\n"
                "Search the web to find real, existing companies or products that "
                "compete with this idea. For each one, report its name, website, "
                "description, strengths, and weaknesses based only on what you find."
            )

            response = self.agent.invoke({"messages": [("user", instruction)]})
            structured = response.get("structured_response")

            if structured is None:
                raise RuntimeError("LLM did not return structured competitor data.")

            if isinstance(structured, BaseModel):
                structured = structured.model_dump()

            return {
                "status": "success",
                "data": {
                    "startup_idea": startup_idea,
                    "competitors": structured.get("competitors", []),
                },
                "message": "Competitor analysis completed successfully."
            }

        except Exception as e:
            return {
                "status": "error",
                "data": {},
                "message": f"CompetitorAgent error: {str(e)}"
            }
