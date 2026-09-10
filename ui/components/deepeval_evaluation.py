import json
import streamlit as st

def _build_retrieval_context(
    report: dict,
    market_analysis: dict,
) -> list[str]:
    """
    Build the same validation evidence used by the existing DeepEval tests.
    """

    context = []

    context_sources = [
        (
            "Market Analysis",
            market_analysis,
        ),
        (
            "Competitor Analysis",
            report.get("competitor_analysis", []),
        ),
        (
            "SWOT Analysis",
            report.get("swot_analysis", {}),
        ),
        (
            "MVP Recommendation",
            report.get("mvp_recommendation", {}),
        ),
        (
            "GTM Strategy",
            report.get("gtm_strategy", {}),
        ),
    ]

    for name, value in context_sources:
        if value:
            context.append(
                f"{name}:\n"
                f"{json.dumps(value, indent=2, default=str)}"
            )

    return context


def _evaluate_report(
    report: dict,
    market_analysis: dict,
    idea: dict,
):
    """
    Evaluate the already-generated validation report.

    This does NOT regenerate or modify the report.
    """

    from deepeval.test_case import LLMTestCase
    from tests.Evaluation.deepeval_config import (
        answer_relevancy_metric,
        report_quality_metric,
    )

    startup_input = (
        f"Validate a startup idea for "
        f"{idea.get('idea', 'the submitted startup idea')}. "
        f"Target audience: {idea.get('target_audience', 'N/A')}. "
        f"Industry: {idea.get('industry', 'N/A')}. "
        f"Problem Statement: {idea.get('problem', 'N/A')}. "
        f"Proposed Solution: {idea.get('solution', 'N/A')}."
    )

    actual_output = json.dumps(
        report,
        indent=2,
        default=str,
    )

    retrieval_context = _build_retrieval_context(
        report,
        market_analysis,
    )

    if not retrieval_context:
        raise RuntimeError(
            "No validation evidence was available for DeepEval evaluation."
        )

    test_case = LLMTestCase(
        input=startup_input,
        actual_output=actual_output,
        retrieval_context=retrieval_context,
    )

    # ---------------------------------------------------------
    # Reuse existing DeepEval metrics
    # ---------------------------------------------------------

    answer_relevancy_metric.measure(test_case)

    answer_relevancy_score = answer_relevancy_metric.score
    answer_relevancy_reason = answer_relevancy_metric.reason
    answer_relevancy_passed = answer_relevancy_metric.is_successful()

    report_quality_metric.measure(test_case)

    report_quality_score = report_quality_metric.score
    report_quality_reason = report_quality_metric.reason
    report_quality_passed = report_quality_metric.is_successful()

    return {
        "answer_relevancy": {
            "score": answer_relevancy_score,
            "reason": answer_relevancy_reason,
            "passed": answer_relevancy_passed,
        },
        "report_quality": {
            "score": report_quality_score,
            "reason": report_quality_reason,
            "passed": report_quality_passed,
        },
    }


def show_deepeval_evaluation():
    """
    Render the standalone DeepEval evaluation page.
    """

    # ---------------------------------------------------------
    # Get the already-generated validation data
    # ---------------------------------------------------------

    final_state = st.session_state.get(
        "validation_result",
        {},
    ) or {}

    report = final_state.get(
        "report",
        {},
    ) or {}

    market_analysis = final_state.get(
        "market_analysis",
        {},
    ) or {}

    idea = st.session_state.get(
        "idea",
        {},
    ) or {}

    # ---------------------------------------------------------
    # Page Header
    # ---------------------------------------------------------

    st.markdown(
        "## 🤖 DeepEval AI Quality Evaluation"
    )

    st.markdown(
        """
        Evaluate the quality of your generated startup validation
        report using **DeepEval**.
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    st.markdown(
        """
        <div style="
            background: rgba(168, 85, 247, 0.06);
            border: 1px solid #2e1065;
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 18px;
        ">

            <div style="
                color: #e9d5ff;
                font-size: 15px;
                font-weight: 600;
                margin-bottom: 10px;
            ">
                What does DeepEval evaluate?
            </div>

            <div style="
                color: #c4b5fd;
                font-size: 13px;
                line-height: 1.8;
            ">
                <b>Answer Relevancy</b><br>
                Checks whether the generated validation report is
                relevant to the submitted startup idea.

                <br><br>

                <b>Report Quality</b><br>
                Evaluates whether the report is relevant, well-structured,
                grounded in validation evidence, clear, and useful for
                making a startup validation decision.

                <br><br>

                Both metrics use a <b>70% threshold</b>.
                The evaluation runs only when you click the button below.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Validate report availability
    # ---------------------------------------------------------

    if not report:
        st.warning(
            "No validation report is available. "
            "Please generate a validation report first."
        )

        if st.button(
            "← Back to Validation Report",
            use_container_width=True,
        ):
            st.session_state.page = "report"
            st.rerun()

        return

    # ---------------------------------------------------------
    # Evaluation Button
    # ---------------------------------------------------------

    if st.button(
        "🔍 Evaluate Report with DeepEval",
        key="deepeval_evaluate_button",
        use_container_width=True,
        type="primary",
    ):
        with st.spinner(
            "DeepEval is evaluating your validation report..."
        ):
            try:
                results = _evaluate_report(
                    report=report,
                    market_analysis=market_analysis,
                    idea=idea,
                )

                st.session_state.deepeval_results = results
                st.session_state.deepeval_error = None

            except Exception as exc:
                st.session_state.deepeval_results = None
                st.session_state.deepeval_error = str(exc)

    # ---------------------------------------------------------
    # Evaluation Error
    # ---------------------------------------------------------

    error = st.session_state.get(
        "deepeval_error"
    )

    if error:
        st.error(
            f"DeepEval evaluation could not be completed: {error}"
        )

    # ---------------------------------------------------------
    # Evaluation Results
    # ---------------------------------------------------------

    results = st.session_state.get(
        "deepeval_results"
    )

    if results:

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            "### 📊 Evaluation Results"
        )

        answer_result = results["answer_relevancy"]
        quality_result = results["report_quality"]

        col1, col2 = st.columns(2)

        # -----------------------------------------------------
        # Answer Relevancy
        # -----------------------------------------------------

        with col1:

            score = answer_result["score"]

            st.metric(
                "Answer Relevancy",
                f"{score * 100:.1f}%",
            )

            if answer_result["passed"]:
                st.success(
                    "✅ Passed · Threshold 70%"
                )
            else:
                st.warning(
                    "⚠️ Below threshold · 70%"
                )

        # -----------------------------------------------------
        # Report Quality
        # -----------------------------------------------------

        with col2:

            score = quality_result["score"]

            st.metric(
                "Report Quality",
                f"{score * 100:.1f}%",
            )

            if quality_result["passed"]:
                st.success(
                    "✅ Passed · Threshold 70%"
                )
            else:
                st.warning(
                    "⚠️ Below threshold · 70%"
                )

        # -----------------------------------------------------
        # Reasoning
        # -----------------------------------------------------

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander(
            "🧠 View DeepEval Reasoning"
        ):

            st.markdown(
                "**Answer Relevancy**"
            )

            st.write(
                answer_result["reason"]
                or "No reasoning returned."
            )

            st.markdown("---")

            st.markdown(
                "**Report Quality**"
            )

            st.write(
                quality_result["reason"]
                or "No reasoning returned."
            )

    # ---------------------------------------------------------
    # Back to Report
    # ---------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "← Back to Validation Report",
        key="deepeval_back_to_report",
        use_container_width=True,
    ):
        st.session_state.page = "report"
        st.rerun()
