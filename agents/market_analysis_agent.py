"""
Market Analysis Agent.

Input from SharedMemory:
    - startup_idea
    - search_results

Output:
{
    "status": "success",
    "data": {
        "market_analysis": {
            "market_size": "...",
            "target_audience": "...",
            "industry_trends": "...",
            "opportunities": "...",
            "market_potential": "..."
        }
    },
    "message": ""
}
"""

import os
from pathlib import Path
from typing import Any, Dict

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Structured output model
# ---------------------------------------------------------------------

class MarketAnalysis(BaseModel):
    """Structured market analysis, matching prompts/market_analysis_agent.md."""

    market_size: str = Field(
        description="Estimated market size/opportunity, based only on the supplied search results."
    )

    target_audience: str = Field(
        description="The primary target audience/customer segments for this startup idea."
    )

    industry_trends: str = Field(
        description="Relevant industry trends supported by the supplied evidence."
    )

    opportunities: str = Field(
        description="Market opportunities or gaps identified from the evidence."
    )

    market_potential: str = Field(
        description="Overall assessment of market potential, with confidence caveats where evidence is limited."
    )


# ---------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------

class MarketAnalysisAgent:

    def __init__(self, agent=None, model_name: str = None):
        """
        Initialize the Market Analysis Agent.

        Parameters
        ----------
        agent:
            Optional pre-built DeepAgent. Mainly useful for testing.

        model_name:
            Optional Gemini model name. Defaults to the environment
            variable STARTUP_VALIDATOR_MODEL or gemini-2.5-flash.
        """

        self.model_name = model_name or os.getenv(
            "STARTUP_VALIDATOR_MODEL", "gemini-2.5-flash"
        )

        self.system_prompt = self._load_prompt()

        if agent is not None:
            self.agent = agent
        else:
            self.agent = self._build_agent()

    # -------------------------------------------------------------
    # Prompt loading
    # -------------------------------------------------------------

    def _load_prompt(self) -> str:
        project_root = Path(__file__).resolve().parents[1]
        prompt_path = project_root / "prompts" / "market_analysis_agent.md"

        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        return (
            "You are a Market Intelligence Analyst. Synthesize market "
            "viability based only on the supplied evidence. Do not "
            "invent market statistics."
        )

    # -------------------------------------------------------------
    # Create DeepAgent
    # -------------------------------------------------------------

    def _build_agent(self):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "Gemini API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY."
            )

        model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            # See competitor_agent.py for why this is set explicitly:
            # the library's default (max_retries=6) silently allows up
            # to 7 real API calls per logical request, which badly
            # multiplies quota usage on 429s.
            max_retries=1,
        )

        return create_deep_agent(
            model=model,
            tools=[],
            system_prompt=self.system_prompt,
            response_format=MarketAnalysis,
        )

    # -------------------------------------------------------------
    # Run
    # -------------------------------------------------------------

    def run(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        try:
            startup_idea = shared_memory.get("startup_idea", "")
            search_results = shared_memory.get("search_results", "")

            if not startup_idea:
                raise ValueError("Missing required input: startup_idea")

            instruction = (
                f"Perform a market analysis for the startup idea: '{startup_idea}'.\n\n"
                f"Base your analysis ONLY on these web search findings:\n{search_results}\n\n"
                "Do not invent market statistics, TAM/SAM/SOM figures, or growth "
                "rates that are not supported by the findings above."
            )

            response = self.agent.invoke({"messages": [("user", instruction)]})

            structured_result = response.get("structured_response")

            if structured_result is None:
                raise RuntimeError("LLM did not return structured market analysis.")

            if isinstance(structured_result, BaseModel):
                structured_result = structured_result.model_dump()

            return {
                "status": "success",
                "data": {"market_analysis": structured_result},
                "message": "Market analysis completed successfully.",
            }

        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"MarketAnalysisAgent error: {str(e)}",
            }
