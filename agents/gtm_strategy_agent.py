"""
GTM Strategy Agent.

Generates a practical Go-To-Market strategy using the outputs
from the previous agents in the startup validation pipeline.

Input from SharedMemory:
    - startup_idea
    - market_analysis
    - competitor_analysis / competitors
    - swot_analysis
    - mvp_recommendation

Output:
{
    "status": "success",
    "data": {
        "gtm_strategy": {
            "positioning_strategy": "...",
            "pricing_ideas": [...],
            "customer_acquisition_channels": [...],
            "launch_strategy": [...]
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
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# =========================================================
# Structured Output Models
# =========================================================

class PricingIdea(BaseModel):
    """A recommended pricing approach."""

    model: str = Field(
        description="Name of the pricing model."
    )

    reason: str = Field(
        description="Why this pricing model is suitable."
    )


class AcquisitionChannel(BaseModel):
    """A recommended customer acquisition channel."""

    channel: str = Field(
        description="Customer acquisition channel."
    )

    reason: str = Field(
        description="Why this channel is suitable for the target audience."
    )


class GTMStrategy(BaseModel):
    """Structured Go-To-Market strategy."""

    positioning_strategy: str = Field(
        description=(
            "Clear positioning explaining who the startup serves, "
            "the problem it solves, its value proposition, and "
            "how it can differentiate."
        )
    )

    pricing_ideas: list[PricingIdea] = Field(
        description=(
            "Practical pricing approaches suitable for the startup."
        )
    )

    customer_acquisition_channels: list[AcquisitionChannel] = Field(
        description=(
            "Recommended customer acquisition channels and "
            "the reason for each."
        )
    )

    launch_strategy: list[str] = Field(
        description=(
            "A practical sequence of steps for launching and "
            "validating the startup."
        )
    )


# =========================================================
# Agent
# =========================================================

class GTMStrategyAgent:

    def __init__(self, agent=None, model_name=None):
        """
        Initialize the GTM Strategy Agent.

        Parameters
        ----------
        agent:
            Optional pre-built DeepAgent.
            Useful for testing.

        model_name:
            Optional Gemini model name.
            Defaults to STARTUP_VALIDATOR_MODEL or gemini-2.5-flash.
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

    # =====================================================
    # Load System Prompt
    # =====================================================

    def _load_prompt(self):

        project_root = Path(__file__).resolve().parents[1]

        prompt_path = (
            project_root
            / "prompts"
            / "gtm_agent.md"
        )

        if prompt_path.exists():

            return prompt_path.read_text(
                encoding="utf-8"
            )

        return """
You are an experienced startup Go-To-Market strategist.

Generate a practical GTM strategy containing:

- Positioning strategy
- Pricing ideas
- Customer acquisition channels
- Launch strategy

Use only the information provided.

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
            max_retries=1,
        )

        return create_deep_agent(
            model=model,
            system_prompt=self.system_prompt,
            response_format=GTMStrategy,
        )

    # =====================================================
    # Run Agent
    # =====================================================

    def run(self, shared_memory):

        try:

            if shared_memory is None:
                raise ValueError(
                    "shared_memory cannot be None."
                )

            startup_idea = shared_memory.get(
                "startup_idea",
                ""
            )

            market_analysis = shared_memory.get(
                "market_analysis",
                {}
            )

            competitor_analysis = shared_memory.get(
                "competitor_analysis"
            )

            if competitor_analysis is None:
                competitor_analysis = shared_memory.get(
                    "competitors",
                    []
                )

            swot_analysis = shared_memory.get(
                "swot_analysis",
                {}
            )

            mvp_recommendation = shared_memory.get(
                "mvp_recommendation",
                {}
            )

            if not startup_idea:
                raise ValueError(
                    "Missing required input: startup_idea"
                )

            user_input = f"""
Create a practical Go-To-Market strategy for the startup.

STARTUP IDEA:
{json.dumps(startup_idea, indent=2, default=str)}

MARKET ANALYSIS:
{json.dumps(market_analysis, indent=2, default=str)}

COMPETITOR ANALYSIS:
{json.dumps(competitor_analysis, indent=2, default=str)}

SWOT ANALYSIS:
{json.dumps(swot_analysis, indent=2, default=str)}

MVP RECOMMENDATION:
{json.dumps(mvp_recommendation, indent=2, default=str)}

Generate:

1. Positioning Strategy
2. Pricing Ideas
3. Customer Acquisition Channels
4. Launch Strategy

Important rules:

- Use the supplied information.
- Do not invent market statistics.
- Do not invent competitors.
- Do not invent customer numbers.
- Do not recommend every possible marketing channel.
- Select channels that fit the target audience.
- Keep pricing recommendations realistic.
- Keep the launch strategy suitable for an early-stage startup.
- Focus on validating the core value proposition.
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
                    "LLM did not return structured GTM strategy."
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
                    "gtm_strategy": structured_result
                },
                "message": (
                    "GTM strategy generated successfully."
                )
            }

        except Exception as e:

            return {
                "status": "error",
                "data": None,
                "message": str(e)
            }
