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

    def __init__(self, agent=None, model_name: str = None):
        if agent is not None:
            self.agent = agent
            return

        model_name = model_name or os.getenv("STARTUP_VALIDATOR_MODEL", "gemini-2.5-flash")
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            # max_retries defaults to 6 in langchain-google-genai, so an
            # unset value here silently allows up to 7 real API calls
            # for a single logical request. That multiplies quota usage
            # badly on 429s, since retrying an already-rate-limited
            # request doesn't help. max_retries=1 is the library's
            # documented way to make exactly one attempt, no retries.
            max_retries=1,
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

            # Reuse the Web Search Agent's findings as a starting point
            # instead of researching the idea from scratch - the deep
            # agent can still call execute_web_search itself for
            # competitor-specific follow-up queries.
            prior_search_results = shared_memory.get("search_results", "")
            prior_references = shared_memory.get("references", [])

            instruction = (
                f"Find real competitors for this startup idea: '{startup_idea}'.\n\n"
            )

            if prior_search_results:
                instruction += (
                    "A prior web search on this idea already found the "
                    f"following context - use it as a starting point:\n"
                    f"{prior_search_results}\n\n"
                )

            if prior_references:
                instruction += f"Known sources so far: {prior_references}\n\n"

            instruction += (
                "Call execute_web_search now for specific competitor names, "
                "products, and companies - do not just write a todo list or "
                "delegate this task. Then report each real competitor you find, "
                "with its name, website, description, strengths, and weaknesses "
                "based only on what you find."
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
