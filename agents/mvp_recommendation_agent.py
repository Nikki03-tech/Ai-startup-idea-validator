"""
MVP Recommendation Agent.

Recommends and prioritizes the smallest realistic MVP.
"""

import json
import os

from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# =========================================================
# Structured Output Models
# =========================================================

class MVPFeature(BaseModel):

    feature: str = Field(
        description="Name of the product feature."
    )

    reason: str = Field(
        description="Why this feature belongs in this priority level."
    )

    validation_goal: str = Field(
        description=(
            "What startup assumption or customer need "
            "this feature helps validate."
        )
    )


class MVPRecommendation(BaseModel):

    must_have: list[MVPFeature] = Field(
        description="Essential features for the first usable MVP."
    )

    nice_to_have: list[MVPFeature] = Field(
        description="Useful features to consider after MVP validation."
    )

    future_features: list[MVPFeature] = Field(
        description="Features that should be postponed until later."
    )

    prioritization_rationale: str = Field(
        description="Overall explanation of feature prioritization."
    )


# =========================================================
# MVP Recommendation Agent
# =========================================================

class MVPRecommendationAgent:

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
            / "mvp_agent.md"
        )

        if prompt_path.exists():

            return prompt_path.read_text(
                encoding="utf-8"
            )

        return """
You are an experienced startup product manager.

Use the supplied SWOT analysis to recommend
a small and realistic Minimum Viable Product.

Prioritize features into:

- Must Have
- Nice to Have
- Future Features

Do not invent unsupported business facts.
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
            response_format=MVPRecommendation,
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

            swot_analysis = shared_memory.get(
                "swot_analysis"
            )

            if not swot_analysis:

                raise ValueError(
                    "Missing required input: swot_analysis"
                )

            user_input = f"""
Create an MVP recommendation using ONLY
the following SWOT analysis.

SWOT ANALYSIS:

{json.dumps(
    swot_analysis,
    indent=2,
    default=str
)}

Identify the smallest realistic product
that can validate the startup idea.

Prioritize features into:

1. Must Have
2. Nice to Have
3. Future Features

For every feature explain:

- Why it belongs in that priority level.
- What assumption or customer need it helps validate.

Important rules:

- Do not recommend unnecessary features.
- Do not build the entire final product as the MVP.
- Prioritize the smallest feature set capable of testing
  the core startup value proposition.
- Do not invent facts that are not supported by the SWOT analysis.
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
                    "LLM did not return structured MVP recommendation."
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
                    "mvp_recommendation": structured_result
                },
                "message": ""
            }

        except Exception as e:

            return {
                "status": "failed",
                "data": None,
                "message": str(e)
            }
