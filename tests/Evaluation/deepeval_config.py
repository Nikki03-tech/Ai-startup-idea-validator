import os

from dotenv import load_dotenv
from deepeval.models import GeminiModel
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCaseParams

load_dotenv()

# Separate Gemini key for DeepEval evaluation.
# This protects the main application Gemini key/quota.
evaluation_model = GeminiModel(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("DEEPEVAL_GEMINI_API_KEY"),
)

answer_relevancy_metric = AnswerRelevancyMetric(
    threshold=0.7,
    model=evaluation_model,
)

report_quality_metric = GEval(
    name="Report Quality",
    criteria=(
        "Evaluate whether the final startup validation report is relevant, "
        "well-structured, grounded in the provided context, clear, and useful "
        "for making a startup validation decision."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT,
    ],
    threshold=0.7,
    model=evaluation_model,
)

FINAL_REPORT_METRICS = [
    answer_relevancy_metric,
    report_quality_metric,
]
