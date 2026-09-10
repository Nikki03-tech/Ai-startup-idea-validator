"""Orchestrator Agent

Deep agent planner that manages overall execution flow, task assignment, and shared state context.
"""
import os
import time
from pydantic import ValidationError

from app.llm import get_chat_model
from pipeline.graph import graph as validation_graph
from state.memory import SharedMemory
from state.schema import StartupIdea, IdeaExtraction
from tools.planning_tool import create_execution_plan


class Orchestrator:
    """
    Central coordinator for the startup validation workflow.
    """

    # Maps each planning-tool task name to the exact agent-name prefix
    # that pipeline/graph.py's record_error() uses when it logs a
    # failure for that agent.
    TASK_TO_AGENT_NAME = {
        "web_search": "Web Search Agent",
        "market_analysis": "Market Analysis Agent",
        "competitor_analysis": "Competitor Agent",
        "swot_risk_analysis": "SWOT & Risk Agent",
        "mvp_recommendation": "MVP Recommendation Agent",
        "gtm_strategy": "GTM Strategy Agent",
        "report_generation": "Report Agent",
    }

    def __init__(self):
        self.memory = SharedMemory()

        # Holds the execution plan after execute_pipeline() has run
        self.execution_plan = None

        # Holds non-fatal error if extract_startup_idea fails
        self._idea_extraction_error = None

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
        Extract structured information from the startup idea using Gemini 3.6 Flash.
        Includes automatic retries for transient 429 and 500 errors.
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

        model_name = os.getenv("STARTUP_VALIDATOR_MODEL", "gemini-3.6-flash")
        model = get_chat_model(
            model_name=model_name,
            temperature=0.2,
            max_retries=3,
        )
        
        # Retry loop for initial idea extraction
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                idea_extraction = model.with_structured_output(IdeaExtraction).invoke(prompt)
                self.memory.idea_extraction = idea_extraction
                return self.memory.idea_extraction
            except Exception as e:
                err_str = str(e).lower()
                if ("429" in err_str or "500" in err_str or "eof" in err_str) and attempt < max_attempts - 1:
                    sleep_time = 12 * (attempt + 1)
                    print(f"[Orchestrator] Idea extraction failed ({e}). Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    raise e

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

    def execute_pipeline(self):
        """
        Run the validation pipeline with retry logic to avoid 429 and 500 crashes.
        """

        if self.memory.startup_idea is None:
            raise ValueError("No startup idea found. Call receive_request() first.")

        # Non-fatal metadata extraction
        try:
            self.extract_startup_idea()
        except Exception as e:
            self.memory.idea_extraction = None
            self._idea_extraction_error = str(e)

        plan = self.build_execution_plan()

        initial_state = {
            "startup_idea": self.memory.startup_idea.idea,
        }

        # Invoke graph with retry logic for 429 and 500 status codes
        max_attempts = 3
        final_state = {}
        for attempt in range(max_attempts):
            try:
                final_state = validation_graph.invoke(initial_state)
                break
            except Exception as e:
                err_str = str(e).lower()
                if ("429" in err_str or "500" in err_str or "eof" in err_str) and attempt < max_attempts - 1:
                    sleep_time = 15 * (attempt + 1)
                    print(f"[Orchestrator Pipeline] Transient error ({e}). Retrying pipeline in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    # Provide fallback empty dictionary on absolute failure so app doesn't crash
                    final_state = {
                        "errors": [f"Pipeline Execution Error: {str(e)}"]
                    }

        errors = final_state.get("errors", [])

        # Attribute errors to individual steps safely
        for task in plan:
            agent_name = self.TASK_TO_AGENT_NAME.get(task["task"])

            matching_errors = [
                err for err in errors
                if agent_name and err.startswith(f"{agent_name}:")
            ]

            if matching_errors:
                task["status"] = "failed"
                task["error"] = "; ".join(matching_errors)
            else:
                task["status"] = "completed"

        self.execution_plan = plan

        # Safely populate shared memory outputs with empty defaults if keys are missing
        self.memory.search_results = final_state.get("search_results", [])
        self.memory.competitors = final_state.get("competitors", [])
        self.memory.market_analysis = final_state.get("market_analysis", {})
        self.memory.swot_analysis = final_state.get("swot_analysis", {})
        self.memory.mvp_recommendation = final_state.get("mvp_recommendation", {})
        self.memory.gtm_strategy = final_state.get("gtm_strategy", {})
        self.memory.report = final_state.get("report")

        return plan

    def get_final_output(self):
        """Return the complete orchestration output."""

        execution_plan = (
            self.execution_plan
            if self.execution_plan is not None
            else self.build_execution_plan()
        )

        return {
            "startup_idea": (
                self.memory.startup_idea.model_dump()
                if self.memory.startup_idea is not None
                else None
            ),
            "idea_extraction": self.memory.idea_extraction,
            "idea_extraction_error": self._idea_extraction_error,
            "execution_plan": execution_plan,
            "memory": self.memory.model_dump(),
        }

    def get_memory(self):
        """Return shared memory."""

        return self.memory