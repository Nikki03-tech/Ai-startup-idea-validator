"""
Report Agent.

Combines all previous startup validation agent outputs
into one final validation report.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


load_dotenv()


# =========================================================
# Structured Output Model
# =========================================================

class ReportAssessment(BaseModel):
    """LLM-generated assessment for the final validation report."""

    executive_summary: str = Field(
        description="Concise startup validation summary."
    )

    risk_analysis: list = Field(
        description="Important startup risks with severity and mitigation."
    )

    final_validation_score: int = Field(
        ge=0,
        le=100,
        description="Startup validation score from 0 to 100."
    )


# =========================================================
# Report Agent
# =========================================================

class ReportAgent:

    def __init__(self, agent=None, model_name=None):

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
            / "report_agent.md"
        )

        if prompt_path.exists():

            return prompt_path.read_text(
                encoding="utf-8"
            )

        return """
You are an experienced startup validation report writer.

Combine the supplied startup validation agent outputs
into one practical founder-friendly validation report.

Do not invent unsupported facts,
statistics, or competitors.

Generate:

- Executive Summary
- Risk Analysis
- Final Validation Score
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
            response_format=ReportAssessment,
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

            startup_idea = shared_memory.get(
                "startup_idea",
                ""
            )

            market_analysis = shared_memory.get(
                "market_analysis",
                {}
            )

            competitors = shared_memory.get(
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

            gtm_strategy = shared_memory.get(
                "gtm_strategy",
                {}
            )

            references = shared_memory.get(
                "references",
                []
            )

            if not startup_idea:

                raise ValueError(
                    "Missing required input: startup_idea"
                )

            # =================================================
            # Ask LLM only for summary, risks and score
            # =================================================

            user_input = f"""
Create a concise startup validation assessment.

Startup Idea:
{startup_idea}

Market Analysis:
{json.dumps(
    market_analysis,
    indent=2,
    default=str
)}

Competitor Analysis:
{json.dumps(
    competitors,
    indent=2,
    default=str
)}

SWOT Analysis:
{json.dumps(
    swot_analysis,
    indent=2,
    default=str
)}

MVP Recommendation:
{json.dumps(
    mvp_recommendation,
    indent=2,
    default=str
)}

GTM Strategy:
{json.dumps(
    gtm_strategy,
    indent=2,
    default=str
)}

Provide:

1. A concise executive summary.
2. Important startup risks with severity and mitigation.
3. A final validation score from 0 to 100.

Rules:

- Use ONLY the supplied information.
- Do not invent statistics.
- Do not invent competitors.
- Do not invent market data.
- Do not contradict the supplied analysis.
- The score must reflect the supplied evidence.
- The score is not a guarantee of startup success.
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
                    "LLM did not return structured validation report."
                )

            # Convert Pydantic model to dictionary
            if isinstance(
                structured_result,
                BaseModel
            ):

                structured_result = (
                    structured_result.model_dump()
                )

            # =================================================
            # Build final report
            # =================================================

            validation_report = {

                "executive_summary":
                    structured_result.get(
                        "executive_summary",
                        ""
                    ),

                # Preserve original agent output
                "market_analysis":
                    market_analysis,

                "competitor_analysis":
                    competitors,

                "swot_analysis":
                    swot_analysis,

                "risk_analysis":
                    structured_result.get(
                        "risk_analysis",
                        []
                    ),

                "mvp_recommendation":
                    mvp_recommendation,

                "gtm_strategy":
                    gtm_strategy,

                "final_validation_score":
                    structured_result.get(
                        "final_validation_score",
                        0
                    ),

                "references":
                    references,
            }

            return {
                "status": "success",
                "data": {
                    "validation_report":
                        validation_report
                },
                "message": ""
            }

        except Exception as e:

            return {
                "status": "error",
                "data": None,
                "message": str(e)
            }
