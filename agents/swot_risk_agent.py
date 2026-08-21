"""
SWOT & Risk Analysis Agent.

Input from SharedMemory:
    - market_analysis
    - competitors

Output:
{
    "status": "success",
    "data": {
        "swot_analysis": {
            "strengths": [...],
            "weaknesses": [...],
            "opportunities": [...],
            "threats": [...],
            "risks": [
                {
                    "risk": "...",
                    "severity": "...",
                    "mitigation": "..."
                }
            ]
        }
    },
    "message": ""
}
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path
from typing import Literal

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Structured output models
# ---------------------------------------------------------------------

class Risk(BaseModel):
    """A startup execution risk."""

    risk: str = Field(
        description="The specific risk facing the startup."
    )

    severity: Literal["Low", "Medium", "High"] = Field(
        description="Risk severity."
    )

    mitigation: str = Field(
        description="A practical way to reduce or manage the risk."
    )


class SWOTAnalysis(BaseModel):
    """Structured SWOT and risk analysis."""

    strengths: list[str] = Field(
        description="Internal strengths supported by the provided evidence."
    )

    weaknesses: list[str] = Field(
        description="Internal weaknesses supported by the provided evidence."
    )

    opportunities: list[str] = Field(
        description="External opportunities supported by the market evidence."
    )

    threats: list[str] = Field(
        description="External threats supported by the competitor and market evidence."
    )

    risks: list[Risk] = Field(
        description="Important execution risks and their mitigation strategies."
    )


# ---------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------

class SWOTRiskAgent:

    def __init__(self, agent=None, model_name=None):
        """
        Initialize the SWOT & Risk Agent.

        Parameters
        ----------
        agent:
            Optional pre-built DeepAgent. Mainly useful for testing.

        model_name:
            Optional Gemini model name. Defaults to the environment
            variable STARTUP_VALIDATOR_MODEL or gemini-2.5-flash.
        """

        self.model_name = (
            model_name
            or os.getenv(
                "STARTUP_VALIDATOR_MODEL",
                "gemini-2.5-flash"
            )
        )

        self.system_prompt = self._load_prompt()

        if agent is not None:
            self.agent = agent
        else:
            self.agent = self._build_agent()

    # -----------------------------------------------------------------
    # Prompt loading
    # -----------------------------------------------------------------

    def _load_prompt(self):

        project_root = Path(__file__).resolve().parents[1]

        prompt_path = (
            project_root
            / "prompts"
            / "swot_risk_agent.md"
        )

        if prompt_path.exists():
            return prompt_path.read_text(
                encoding="utf-8"
            )

        return """
You are a startup strategy consultant.

Analyze the provided market analysis and competitor analysis.

Generate:
- Strengths
- Weaknesses
- Opportunities
- Threats
- Risks
- Risk mitigation strategies

Do not invent unsupported facts.
"""

    # -----------------------------------------------------------------
    # Create DeepAgent
    # -----------------------------------------------------------------

    def _build_agent(self):

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:
            raise RuntimeError(
                "Gemini API key not found. "
                "Set GOOGLE_API_KEY or GEMINI_API_KEY."
            )

        model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=0.2,
            max_retries=1,
        )

        return create_deep_agent(
            model=model,
            system_prompt=self.system_prompt,
            response_format=SWOTAnalysis,
        )

    # -----------------------------------------------------------------
    # Run
    # -----------------------------------------------------------------

    def run(self, shared_memory):

        try:

            if shared_memory is None:
                raise ValueError(
                    "shared_memory cannot be None."
                )

            market_analysis = shared_memory.get(
                "market_analysis"
            )

            competitors = shared_memory.get(
                "competitors"
            )

            if not market_analysis:
                raise ValueError(
                    "Missing required input: market_analysis"
                )

            if not competitors:
                raise ValueError(
                    "Missing required input: competitors"
                )

            # Only the required inputs are passed to this agent.
            def build_user_input(extra_emphasis: str = "") -> str:
                return f"""
Analyze the startup using ONLY the following information.

MARKET ANALYSIS:
{json.dumps(market_analysis, indent=2, default=str)}

COMPETITOR ANALYSIS:
{json.dumps(competitors, indent=2, default=str)}

Produce a practical SWOT and risk analysis.

Important rules:

1. Strengths and weaknesses must describe internal characteristics.
2. Opportunities and threats must describe external factors.
3. Risks must focus on realistic execution or business risks.
4. Every risk must have Low, Medium, or High severity.
5. Every risk must have a practical mitigation strategy.
6. Do not invent market statistics, competitors, companies, or facts
   that are not supported by the supplied information.
7. If evidence is limited, make conservative inferences rather than
   inventing facts.
8. Do NOT write a todo list or delegate this to a subagent. Analyze
   the information above yourself and answer directly. Your response
   must contain the actual strengths, weaknesses, opportunities, and
   threats - not a plan, and not an empty list, unless the supplied
   evidence genuinely contains nothing relevant to that category.
{extra_emphasis}"""

            def invoke_agent(user_input: str):
                result = self.agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_input,
                            }
                        ]
                    }
                )

                structured_result = result.get(
                    "structured_response"
                )

                if structured_result is None:
                    raise RuntimeError(
                        "LLM did not return structured SWOT analysis."
                    )

                if isinstance(
                    structured_result,
                    BaseModel
                ):
                    structured_result = (
                        structured_result.model_dump()
                    )

                return structured_result

            structured_result = invoke_agent(
                build_user_input()
            )

            # ---------------------------------------------------------
            # Defensive retry: DeepAgents can sometimes stop after only
            # writing a plan instead of doing the actual analysis, which
            # yields a structurally valid but substantively empty SWOT
            # (all four categories empty) even though real market/
            # competitor evidence was supplied. When that happens, retry
            # once with a stronger, more explicit instruction rather than
            # silently returning an empty analysis.
            # ---------------------------------------------------------

            core_fields = (
                "strengths",
                "weaknesses",
                "opportunities",
                "threats",
            )

            is_empty = all(
                not structured_result.get(field)
                for field in core_fields
            )

            if is_empty:

                retry_emphasis = (
                    "\nYour previous attempt returned an empty "
                    "analysis even though real market and competitor "
                    "evidence was supplied above. Re-read that "
                    "evidence carefully and produce actual, specific "
                    "strengths, weaknesses, opportunities, and threats "
                    "grounded in it. Do not return empty lists again "
                    "unless the evidence truly supports none."
                )

                structured_result = invoke_agent(
                    build_user_input(retry_emphasis)
                )

            return {
                "status": "success",
                "data": {
                    "swot_analysis": structured_result
                },
                "message": ""
            }

        except Exception as e:

            return {
                "status": "error",
                "data": None,
                "message": str(e)
            }
