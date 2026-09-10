"""
End-to-end DeepEval tests for the final startup validation report.

The real startup validation pipeline is executed for each evaluation
startup idea. DeepEval then evaluates the final validation report.

DeepEval is intentionally NOT applied to:
- individual agents
- Conversational Advisor
- FastAPI
- PostgreSQL
- UI/widget responses

It evaluates only the final validation output.
"""

import json

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from app.orchestrator import Orchestrator

from tests.evaluation.deepeval_config import (
    FINAL_REPORT_METRICS,
)

from tests.evaluation.evaluation_dataset import (
    EVALUATION_GOLDENS,
)


# =========================================================
# Helpers
# =========================================================

def run_validation_pipeline(startup_idea: str):
    """
    Run the actual startup validation pipeline and return
    the complete orchestration output.
    """

    orchestrator = Orchestrator()

    orchestrator.receive_request(
        idea=startup_idea
    )

    orchestrator.execute_pipeline()

    return orchestrator.get_final_output()


def build_final_report_output(orchestration_output: dict) -> str:
    """
    Convert the final validation report into a text representation
    suitable for DeepEval's actual_output field.
    """

    memory = orchestration_output.get(
        "memory",
        {}
    )

    report = memory.get(
        "report"
    )

    if report is None:
        raise RuntimeError(
            "Validation pipeline completed but no final report "
            "was returned."
        )

    if isinstance(report, str):
        return report

    return json.dumps(
        report,
        indent=2,
        default=str,
    )


def build_retrieval_context(orchestration_output: dict) -> list[str]:
    """
    Build the evidence/context used to evaluate whether the final
    report is grounded in the outputs of the validation pipeline.

    This is intentionally based on the real intermediate outputs,
    rather than fabricated reference answers.
    """

    memory = orchestration_output.get(
        "memory",
        {}
    )

    context = []

    context_sources = [
        (
            "Market Analysis",
            memory.get(
                "market_analysis",
                {}
            ),
        ),
        (
            "Competitor Analysis",
            memory.get(
                "competitors",
                []
            ),
        ),
        (
            "SWOT Analysis",
            memory.get(
                "swot_analysis",
                {}
            ),
        ),
        (
            "MVP Recommendation",
            memory.get(
                "mvp_recommendation",
                {}
            ),
        ),
        (
            "GTM Strategy",
            memory.get(
                "gtm_strategy",
                {}
            ),
        ),
    ]

    for name, value in context_sources:

        if not value:
            continue

        context.append(
            f"{name}:\n"
            f"{json.dumps(value, indent=2, default=str)}"
        )

    if not context:
        raise RuntimeError(
            "No intermediate validation evidence was available "
            "to evaluate the final report."
        )

    return context


# =========================================================
# DeepEval Test
# =========================================================

@pytest.mark.parametrize(
    "golden",
    EVALUATION_GOLDENS,
)
def test_final_validation_report(golden):

    # -----------------------------------------------------
    # Run the actual application
    # -----------------------------------------------------

    orchestration_output = run_validation_pipeline(
        golden.input
    )

    # -----------------------------------------------------
    # Extract final output
    # -----------------------------------------------------

    actual_output = build_final_report_output(
        orchestration_output
    )

    # -----------------------------------------------------
    # Build supporting evidence
    # -----------------------------------------------------

    retrieval_context = build_retrieval_context(
        orchestration_output
    )

    # -----------------------------------------------------
    # Create DeepEval test case
    # -----------------------------------------------------

    test_case = LLMTestCase(
        input=golden.input,
        actual_output=actual_output,
        retrieval_context=retrieval_context,
    )

    # -----------------------------------------------------
    # Evaluate final validation report
    # -----------------------------------------------------

    assert_test(
        test_case=test_case,
        metrics=FINAL_REPORT_METRICS,
        run_async=True,
    )
