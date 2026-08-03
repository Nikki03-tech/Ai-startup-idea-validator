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
        Extract structured information from the startup idea using Gemini.
        """

        if self.memory.startup_idea is None:
            raise ValueError("No startup idea found. Call receive_request() first.")

        prompt = f"""
Analyze the following startup idea.

Startup Idea:
{self.memory.startup_idea.idea}

Extract the following:

- Problem
- Solution
- Target Audience
- Value Proposition
- Keywords

Return the response as structured JSON.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
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
        """
        Placeholder for agent execution.
        Will be connected to actual agents later.
        """

        print(f"Executing: {task_name}")

    def execute_pipeline(self):
        """
        Execute the validation pipeline sequentially.
        """

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
        """
        Return the complete orchestration output.
        """

        return {
            "startup_idea": self.memory.startup_idea,
            "idea_extraction": self.memory.idea_extraction,
            "execution_plan": self.build_execution_plan(),
            "memory": self.memory.model_dump(),
        }

    def get_memory(self):
        """Return shared memory."""

        return self.memory