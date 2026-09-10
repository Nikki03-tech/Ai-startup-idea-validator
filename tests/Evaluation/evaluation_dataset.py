"""
Evaluation dataset for the AI Startup Idea Validator.

The dataset contains representative startup ideas that are used
to evaluate the final validation report.

We intentionally do NOT hard-code expected validation reports.
The validation report is generated dynamically by the actual
multi-agent pipeline and is evaluated by DeepEval afterward.
"""

from deepeval.dataset import EvaluationDataset, Golden


# =========================================================
# Evaluation Goldens
# =========================================================

EVALUATION_GOLDENS = [
    Golden(
        input=(
            "Validate a startup idea for an AI-powered crop health "
            "monitoring platform that uses satellite imagery to help "
            "farmers identify crop stress and take timely action."
        ),
    ),

    Golden(
        input=(
            "Validate a startup idea for an AI-powered resume and "
            "job application assistant that helps students and "
            "fresh graduates improve resumes and prepare for job "
            "applications."
        ),
    ),

    Golden(
        input=(
            "Validate a startup idea for a smart EV charging platform "
            "that helps electric vehicle owners find available "
            "charging stations and optimize charging based on "
            "location and demand."
        ),
    ),

    Golden(
        input=(
            "Validate a startup idea for an AI-powered personal "
            "finance assistant that helps young professionals track "
            "expenses, understand spending patterns, and create "
            "simple savings plans."
        ),
    ),

    Golden(
        input=(
            "Validate a startup idea for a platform that connects "
            "local small businesses with customers through AI-based "
            "personalized offers and recommendations."
        ),
    ),
]


# =========================================================
# Evaluation Dataset
# =========================================================

evaluation_dataset = EvaluationDataset(
    goldens=EVALUATION_GOLDENS
)


# =========================================================
# Helper
# =========================================================

def get_evaluation_goldens() -> list[Golden]:
    """
    Return the startup ideas used for evaluation.

    Goldens are converted into LLMTestCases later, after the
    actual validation pipeline generates the final report.
    """

    return EVALUATION_GOLDENS
