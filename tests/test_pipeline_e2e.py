"""End-to-End Pipeline Integration Tests.

Runs the full LangGraph pipeline (pipeline/graph.py) with every agent's
run() method mocked, so this test needs no live LLM/API access and no
API keys. It exercises the real node wiring - including the
gtm_strategy/report unwrapping logic - end to end.
"""

import os
import sys
from unittest import mock

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# The module-level agent instances in pipeline.graph build real
# ChatGoogleGenerativeAI clients at import time, so a dummy key is
# enough (no network call happens until .invoke()/.run() is called,
# and we mock those below).
os.environ.setdefault("GEMINI_API_KEY", "dummy_key_for_tests")

from pipeline import graph as graph_module


FAKE_WEB_SEARCH = {
    "status": "success",
    "data": {"search_results": "mock search summary", "references": ["https://a.com"]},
    "message": "",
}
FAKE_MARKET = {
    "status": "success",
    "data": {
        "market_analysis": {
            "market_size": "Large",
            "target_audience": "Students",
            "industry_trends": "Growing",
            "opportunities": "Gap in the market",
            "market_potential": "High",
        }
    },
    "message": "",
}
FAKE_COMPETITOR = {
    "status": "success",
    "data": {
        "startup_idea": "idea",
        "competitors": [
            {"name": "Acme", "strengths": ["brand"], "weaknesses": ["price"]}
        ],
    },
    "message": "",
}
FAKE_SWOT = {
    "status": "success",
    "data": {
        "swot_analysis": {
            "strengths": ["s1"],
            "weaknesses": ["w1"],
            "opportunities": ["o1"],
            "threats": ["t1"],
            "risks": [{"risk": "r1", "severity": "Medium", "mitigation": "m1"}],
        }
    },
    "message": "",
}
FAKE_MVP = {
    "status": "success",
    "data": {
        "mvp_recommendation": {
            "must_have": [{"feature": "auth"}],
            "nice_to_have": [],
            "future_features": [],
            "prioritization_rationale": "focus",
        }
    },
    "message": "",
}
FAKE_GTM = {
    "status": "success",
    "data": {
        "gtm_strategy": {
            "positioning_strategy": "niche first",
            "pricing_ideas": [],
            "customer_acquisition_channels": [{"channel": "SEO"}],
            "launch_strategy": ["soft launch"],
        }
    },
    "message": "",
}
FAKE_REPORT = {
    "status": "success",
    "data": {
        "validation_report": {
            "executive_summary": "Looks promising.",
            "market_analysis": {},
            "competitor_analysis": [],
            "swot_analysis": {},
            "risk_analysis": [],
            "mvp_recommendation": {},
            "gtm_strategy": {},
            "final_validation_score": 72,
            "references": [],
        }
    },
    "message": "",
}


def _run_pipeline():
    with mock.patch.object(graph_module.web_search_agent, "run", return_value=FAKE_WEB_SEARCH), \
         mock.patch.object(graph_module.market_agent, "run", return_value=FAKE_MARKET), \
         mock.patch.object(graph_module.competitor_agent, "run", return_value=FAKE_COMPETITOR), \
         mock.patch.object(graph_module.swot_agent, "run", return_value=FAKE_SWOT), \
         mock.patch.object(graph_module.mvp_agent, "run", return_value=FAKE_MVP), \
         mock.patch.object(graph_module.gtm_agent, "run", return_value=FAKE_GTM), \
         mock.patch.object(graph_module.report_agent, "run", return_value=FAKE_REPORT):

        return graph_module.graph.invoke({"startup_idea": "An AI startup idea validator."})


def test_pipeline_runs_without_errors():
    final_state = _run_pipeline()
    assert final_state.get("errors", []) == []


def test_pipeline_wires_every_node_output_into_state():
    final_state = _run_pipeline()

    assert final_state["search_results"] == "mock search summary"
    assert final_state["references"] == ["https://a.com"]
    assert final_state["market_analysis"]["market_size"] == "Large"
    assert final_state["competitors"][0]["name"] == "Acme"
    assert final_state["swot_analysis"]["strengths"] == ["s1"]
    assert final_state["mvp_recommendation"]["must_have"][0]["feature"] == "auth"


def test_gtm_strategy_is_not_double_nested():
    """Regression test for the Phase 4 fix in gtm_node."""
    final_state = _run_pipeline()

    gtm = final_state["gtm_strategy"]
    assert "positioning_strategy" in gtm
    assert "gtm_strategy" not in gtm


def test_report_is_not_double_nested():
    """Regression test for the Phase 4 fix in report_node."""
    final_state = _run_pipeline()

    report = final_state["report"]
    assert "executive_summary" in report
    assert report["final_validation_score"] == 72
    assert "validation_report" not in report
