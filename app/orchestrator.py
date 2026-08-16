"""Orchestrator Agent

Deep agent planner that manages overall execution flow, task assignment, and shared state context.
"""
from google import genai

from app.config import settings
from state.memory import SharedMemory
from state.schema import StartupIdea, IdeaExtraction
from tools.planning_tool import create_execution_plan


class Orchestrator:
    """
    Central coordinator for the startup validation workflow.
    """

    def __init__(self):
        self.memory = SharedMemory()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def receive_request(
        self,
        idea: str,
        target_audience: str = "",
        industry: str = "",
        constraints: list[str] | None = None,
    ):
        """Store the startup idea in shared memory."""
        self.memory.startup_idea = StartupIdea(
            idea=idea,
            target_audience=target_audience,
            industry=industry,
            constraints=constraints or [],
        )

    def extract_startup_idea(self):
        """
        Extract structured information and generate dynamic startup evaluation using Gemini.
        """
        if self.memory.startup_idea is None:
            raise ValueError("No startup idea found. Call receive_request() first.")

        prompt = f"""
Analyze and evaluate the following startup idea thoroughly.

Startup Details:
- Idea: {self.memory.startup_idea.idea}
- Industry: {self.memory.startup_idea.industry}
- Target Audience: {self.memory.startup_idea.target_audience}

Provide a realistic assessment including:
1. Problem & Solution summary.
2. Target Audience & Value Proposition.
3. Relevant keywords.
4. Validation score from 0 to 100 based on market viability.
5. Market Potential ("High", "Medium", or "Low") and Risk Level ("High", "Medium", or "Low").
6. SWOT analysis lists (2-3 tailored bullet points per category).
7. Actionable Go-To-Market (GTM) strategy targeted at this exact audience.
"""

        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": IdeaExtraction,
            },
        )

        self.memory.idea_extraction = response.parsed
        return self.memory.idea_extraction

    def build_execution_plan(self):
        """Create the workflow execution plan."""
        tasks = [
            "web_search",
            "market_analysis",
            "competitor_analysis",
            "swot_risk_analysis",
            "mvp_recommendation",
            "gtm_strategy",
            "report_generation",
        ]
        return create_execution_plan(tasks)

    def delegate_task(self, task_name: str):
        """Placeholder for agent execution."""
        print(f"Executing: {task_name}")

    def execute_pipeline(self):
        """Execute the validation pipeline sequentially."""
        plan = self.build_execution_plan()
        for task in plan:
            try:
                self.delegate_task(task["task"])
                task["status"] = "completed"
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                break
        return plan

    def get_final_output(self):
        """Return the complete orchestration output."""
        return {
            "startup_idea": self.memory.startup_idea,
            "idea_extraction": self.memory.idea_extraction,
            "execution_plan": self.build_execution_plan(),
            "memory": self.memory.model_dump(),
        }

    def get_memory(self):
        """Return shared memory."""
        return self.memory


def run_analysis(idea_data: dict) -> dict:
    """Wrapper function to execute dynamic Orchestrator flow from Streamlit UI."""
    orchestrator = Orchestrator()

    orchestrator.receive_request(
        idea=idea_data.get("idea", idea_data.get("startup_name", "")),
        target_audience=idea_data.get("target_audience", ""),
        industry=idea_data.get("industry", ""),
    )

    extraction = orchestrator.extract_startup_idea()
    pipeline_result = orchestrator.execute_pipeline()

    # Convert evaluation lists to Markdown bullet strings
    strengths_md = "\n".join([f"- {item}" for item in extraction.strengths])
    weaknesses_md = "\n".join([f"- {item}" for item in extraction.weaknesses])
    opportunities_md = "\n".join([f"- {item}" for item in extraction.opportunities])
    threats_md = "\n".join([f"- {item}" for item in extraction.threats])

    return {
        "score": extraction.validation_score,
        "market_potential": extraction.market_potential,
        "risk_level": extraction.risk_level,
        "swot": {
            "strengths": strengths_md,
            "weaknesses": weaknesses_md,
            "opportunities": opportunities_md,
            "threats": threats_md,
        },
        "mvp_recommendation": extraction.solution,
        "gtm_strategy": extraction.gtm_strategy,
        "raw_pipeline": pipeline_result,
    }