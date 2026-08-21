"""Orchestrator Agent

Deep agent planner that manages overall execution flow, task assignment, and shared state context.
"""
import os

from google import genai
from pydantic import ValidationError

from app.config import settings
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
    # failure for that agent (see graph.py's per-node except/else
    # blocks). Used to attribute pipeline errors back to the specific
    # step that produced them instead of marking every step the same.
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
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Holds the execution plan *after* execute_pipeline() has run,
        # with each step's real status ("completed"/"failed") filled
        # in. get_final_output() returns this (instead of rebuilding a
        # fresh all-"pending" plan) so completed runs are reported
        # accurately.
        self.execution_plan = None

        # Set if extract_startup_idea() fails inside execute_pipeline();
        # surfaced in get_final_output() so a failure is visible instead
        # of silently leaving idea_extraction as null with no trace.
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
        Extract structured information from the startup idea using Gemini.

        Uses the same STARTUP_VALIDATOR_MODEL env var as the rest of
        the pipeline (default gemini-2.5-flash) instead of a hardcoded
        model, so this step actually exercises whichever Gemini
        version the project is configured to test.
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

        model_name = os.getenv("STARTUP_VALIDATOR_MODEL", "gemini-2.5-flash")

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": IdeaExtraction,
            },
        )

        idea_extraction = response.parsed

        # Some model/SDK combinations can return valid JSON text but
        # leave `.parsed` empty (e.g. if structured-output parsing
        # isn't fully supported for a given model yet). Fall back to
        # parsing `.text` ourselves rather than silently losing the
        # extraction.
        if idea_extraction is None and getattr(response, "text", None):
            try:
                idea_extraction = IdeaExtraction.model_validate_json(
                    response.text
                )
            except (ValidationError, ValueError) as parse_error:
                raise RuntimeError(
                    "Gemini returned a response for idea extraction, "
                    "but it could not be parsed as structured JSON "
                    f"matching IdeaExtraction: {parse_error}"
                ) from parse_error

        if idea_extraction is None:
            raise RuntimeError(
                "Gemini did not return a usable response for idea "
                "extraction (no parsed structured output and no "
                "response text)."
            )

        self.memory.idea_extraction = idea_extraction

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

    def execute_pipeline(self):
        """
        Run the validation pipeline.

        This does NOT reimplement agent execution. It builds a plan for
        tracking/display purposes and then delegates the actual work to
        the compiled LangGraph workflow in pipeline/graph.py, which is
        the single source of truth for how the seven agents run and
        hand off state to one another.
        """

        if self.memory.startup_idea is None:
            raise ValueError("No startup idea found. Call receive_request() first.")

        # extract_startup_idea() previously existed but was never
        # called anywhere in the app, so self.memory.idea_extraction
        # was always None/null regardless of Gemini model. Call it
        # here so idea_extraction is actually populated. This is
        # supplementary metadata for the report/UI - it is not
        # consumed by pipeline/graph.py's nodes - so a failure here
        # must not abort the real validation pipeline; it's recorded
        # as a non-fatal error instead.
        try:
            self.extract_startup_idea()
        except Exception as e:
            self.memory.idea_extraction = None
            self._idea_extraction_error = str(e)

        plan = self.build_execution_plan()

        initial_state = {
            "startup_idea": self.memory.startup_idea.idea,
        }

        final_state = validation_graph.invoke(initial_state)

        errors = final_state.get("errors", [])

        # Attribute each error to the specific step that produced it
        # (record_error() in pipeline/graph.py prefixes every error
        # with "<Agent Name>: ..."), rather than marking every task as
        # failed just because *some* agent in the run failed.
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

        # Keep the fully-updated plan around so get_final_output()
        # reflects the real outcome of this run instead of rebuilding
        # a fresh, all-"pending" plan.
        self.execution_plan = plan

        # Store the graph's outputs back into shared memory so
        # get_final_output()/get_memory() reflect the real pipeline run.
        self.memory.search_results = final_state.get("search_results", [])
        self.memory.competitors = final_state.get("competitors", [])
        self.memory.market_analysis = final_state.get("market_analysis", {})
        self.memory.swot_analysis = final_state.get("swot_analysis", {})
        self.memory.mvp_recommendation = final_state.get("mvp_recommendation", {})
        self.memory.gtm_strategy = final_state.get("gtm_strategy", {})
        self.memory.report = final_state.get("report")

        return plan

    def get_final_output(self):
        """
        Return the complete orchestration output.

        If execute_pipeline() has already run, this returns the plan
        with each step's real status ("completed"/"failed") as
        determined by the actual LangGraph run - not a freshly built
        plan, which would incorrectly show every step as "pending"
        even after a successful run.
        """

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
