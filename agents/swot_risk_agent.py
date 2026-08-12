"""
SWOT & Risk Analysis Agent.
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


# =========================================================
# Structured Output Models
# =========================================================

class Risk(BaseModel):
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
    strengths: list[str] = Field(
        description="Internal strengths supported by the evidence."
    )

    weaknesses: list[str] = Field(
        description="Internal weaknesses supported by the evidence."
    )

    opportunities: list[str] = Field(
        description="External opportunities supported by the evidence."
    )

    threats: list[str] = Field(
        description="External threats supported by the evidence."
    )

    risks: list[Risk] = Field(
        description="Important execution risks and mitigation strategies."
    )


# =========================================================
# SWOT Risk Agent
# =========================================================

class SWOTRiskAgent:

    def __init__(self, agent=None, model_name=None):

        self.model_name = (
            model_name
            or os.getenv(
                "STARTUP_VALIDATOR_MODEL",
                "gemini-flash-latest"
            )
        )

        self.system_prompt = self._load_prompt()

        if agent is not None:
            self.agent = agent
        else:
            self.agent = self._build_agent()

    # =====================================================
    # Load System Prompt
    # =====================================================

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

Analyze the supplied market and competitor information.

Generate:

- Strengths
- Weaknesses
- Opportunities
- Threats
- Risks
- Risk severity
- Risk mitigation

Do not invent unsupported facts.
"""

    # =====================================================
    # Build DeepAgent
    # =====================================================

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
            max_retries=2,
        )

        return create_deep_agent(
            model=model,
            system_prompt=self.system_prompt,
            response_format=SWOTAnalysis,
        )

    # =====================================================
    # Run
    # =====================================================

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

            user_input = f"""
Analyze the startup using ONLY the information below.

MARKET ANALYSIS:
{json.dumps(
    market_analysis,
    indent=2,
    default=str
)}

COMPETITOR ANALYSIS:
{json.dumps(
    competitors,
    indent=2,
    default=str
)}

Produce a practical SWOT and risk analysis.

Rules:

1. Strengths and weaknesses are internal.
2. Opportunities and threats are external.
3. Risks must be realistic execution or business risks.
4. Every risk must have Low, Medium, or High severity.
5. Every risk must have a practical mitigation.
6. Do not invent statistics, competitors, companies, or facts.
7. If evidence is limited, make conservative inferences.
"""

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

            return {
                "status": "success",
                "data": {
                    "swot_analysis": structured_result
                },
                "message": ""
            }

        except Exception as e:

            return {
                "status": "failed",
                "data": None,
                "message": str(e)
            }