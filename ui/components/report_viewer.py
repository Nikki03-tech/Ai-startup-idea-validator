import streamlit as st
from ui.components.pdf_generator import generate_pdf_report

def _bullets(items):
    """Render a list of strings (or dicts with a 'feature'/'risk' key) as markdown bullets."""

    if not items:
        st.markdown("_None reported._")
        return

    for item in items:
        if isinstance(item, dict):
            text = item.get("feature") or item.get("risk") or item.get("channel") or item.get("model") or str(item)
            st.markdown(f"- {text}")
        else:
            st.markdown(f"- {item}")


def _idea_recap(idea: dict):
    with st.container(border=True):
        st.markdown("#### ðŸ“ What you submitted")

        st.markdown(f"**Startup Idea:** {idea.get('idea') or '_Not provided._'}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Target Audience:** {idea.get('target_audience') or 'N/A'}")
        with c2:
            st.markdown(f"**Industry:** {idea.get('industry') or 'N/A'}")

        st.markdown(f"**Problem Statement:** {idea.get('problem') or 'N/A'}")
        st.markdown(f"**Proposed Solution:** {idea.get('solution') or 'N/A'}")


def _overview_tab(report: dict, market_analysis: dict, idea: dict):
    score = report.get("final_validation_score")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Validation Score", f"{score}/100" if score is not None else "N/A")
    with m2:
        st.metric("Competitors Found", len(report.get("competitor_analysis", []) or []))
    with m3:
        risk_count = len((report.get("swot_analysis") or {}).get("risks", []) or [])
        st.metric("Risks Identified", risk_count)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### ðŸ“ Executive Summary")
    st.write(report.get("executive_summary") or "_Not available._")

    st.markdown("<br>", unsafe_allow_html=True)
    _idea_recap(idea)


def _market_and_competitors_tab(report: dict, market_analysis: dict):
    st.markdown("#### ðŸ“ˆ Market Analysis")
    with st.container(border=True):
        if market_analysis:
            st.markdown(f"**Market Size:** {market_analysis.get('market_size', 'N/A')}")
            st.markdown(f"**Target Audience:** {market_analysis.get('target_audience', 'N/A')}")
            st.markdown(f"**Industry Trends:** {market_analysis.get('industry_trends', 'N/A')}")
            st.markdown(f"**Opportunities:** {market_analysis.get('opportunities', 'N/A')}")
            st.markdown(f"**Market Potential:** {market_analysis.get('market_potential', 'N/A')}")
        else:
            st.markdown("_Not available._")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### ðŸ¢ Competitor Analysis")
    competitors = report.get("competitor_analysis") or []
    if not competitors:
        st.markdown("_No competitors found._")
    for competitor in competitors:
        name = competitor.get("name", "Unknown") if isinstance(competitor, dict) else str(competitor)
        with st.expander(f"ðŸ³ï¸ {name}"):
            if isinstance(competitor, dict):
                st.write(competitor.get("description", ""))
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Strengths**")
                    _bullets(competitor.get("strengths", []))
                with col2:
                    st.markdown("**Weaknesses**")
                    _bullets(competitor.get("weaknesses", []))


def _swot_tab(report: dict):
    swot = report.get("swot_analysis") or {}

    st.markdown("#### ðŸ“Š SWOT Analysis")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**ðŸ’ª Strengths**")
            _bullets(swot.get("strengths", []))
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**ðŸŒ± Opportunities**")
            _bullets(swot.get("opportunities", []))
    with col2:
        with st.container(border=True):
            st.markdown("**âš ï¸ Weaknesses**")
            _bullets(swot.get("weaknesses", []))
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**ðŸš¨ Threats**")
            _bullets(swot.get("threats", []))

    risks = swot.get("risks", [])
    if risks:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ðŸ›¡ï¸ Risks & Mitigation")
        for risk in risks:
            severity = risk.get("severity", "N/A")
            with st.container(border=True):
                st.markdown(
                    f"**{risk.get('risk', 'Unknown risk')}**  \n"
                    f"Severity: `{severity}`  \n"
                    f"Mitigation: {risk.get('mitigation', 'N/A')}"
                )


def _mvp_and_gtm_tab(report: dict):
    st.markdown("#### ðŸ’¡ MVP Recommendation")
    mvp = report.get("mvp_recommendation") or {}
    with st.container(border=True):
        st.markdown("**Must Have**")
        _bullets(mvp.get("must_have", []))
        st.markdown("**Nice to Have**")
        _bullets(mvp.get("nice_to_have", []))
        if mvp.get("prioritization_rationale"):
            st.markdown("**Prioritization Rationale**")
            st.write(mvp["prioritization_rationale"])

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### ðŸš€ Go-To-Market Strategy")
    gtm = report.get("gtm_strategy") or {}
    with st.container(border=True):
        if gtm.get("positioning_strategy"):
            st.write(gtm["positioning_strategy"])
        st.markdown("**Customer Acquisition Channels**")
        _bullets(gtm.get("customer_acquisition_channels", []))
        st.markdown("**Launch Strategy**")
        _bullets(gtm.get("launch_strategy", []))


def _actions_row(report: dict):
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        pdf_bytes = generate_pdf_report(
            report,
            st.session_state.get("idea", {}),
        )

        st.download_button(
            "ðŸ“„ Generate & Download PDF",
            data=pdf_bytes,
            file_name="startup_validation_report.pdf",
            mime="application/pdf",
            use_container_width=True,
       )

    with col2:
        if st.button("ðŸ’¬ Ask a Follow-up Question", use_container_width=True):
            st.session_state.page = "advisor"
            st.rerun()

    with col3:
        if st.button("ðŸ”„ Validate Another Idea", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.pop("validation_result", None)
            st.session_state.pop("idea", None)
            st.rerun()


def show_report():
    idea = st.session_state.get("idea", {})
    final_state = st.session_state.get("validation_result", {}) or {}

    st.markdown(
        f"<h1>ðŸ“ˆ Validation Report: {idea.get('display_title', 'Your Startup')}</h1>",
        unsafe_allow_html=True,
    )

    errors = final_state.get("errors", [])
    report = final_state.get("report", {}) or {}

    if errors and not report:
        st.error("The validation pipeline did not complete successfully.")
        for err in errors:
            st.markdown(f"- {err}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ðŸ”„ Try Again", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        return

    if errors:
        st.warning("Report generated, but some agents reported issues: " + "; ".join(errors))
    else:
        st.success("Validation completed successfully!")

    st.markdown("<br>", unsafe_allow_html=True)

    market_analysis = final_state.get("market_analysis") or {}

    tab_overview, tab_market, tab_swot, tab_mvp_gtm = st.tabs(
        ["Overview", "Market & Competitors", "SWOT & Risk", "MVP & GTM"]
    )

    with tab_overview:
        _overview_tab(report, market_analysis, idea)

    with tab_market:
        _market_and_competitors_tab(report, market_analysis)

    with tab_swot:
        _swot_tab(report)

    with tab_mvp_gtm:
        _mvp_and_gtm_tab(report)

    _actions_row(report)
