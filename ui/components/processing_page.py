import time

import streamlit as st

from pipeline.graph import graph


# Node names match pipeline/graph.py's add_node() calls, in the order
# the graph actually executes them. This list drives the checklist
# below and is only used for display labels/ordering - the actual
# execution order and results always come from the real graph.
STAGES = [
    ("web_search", "Web Search"),
    ("market_analysis", "Market Analysis"),
    ("competitor_analysis", "Competitor Research"),
    ("swot_analysis", "SWOT & Risk Analysis"),
    ("mvp_recommendation", "MVP Recommendation"),
    ("gtm_strategy", "GTM Strategy"),
    ("report_generation", "Report Generation"),
]


def _render_checklist(container, completed_nodes: set, current_node: str | None):
    """
    Render the âœ“ / â³ / â—‹ agent checklist for the stages that have
    actually completed (or are actively running) in the real graph
    run so far - never a simulated/fixed animation.
    """

    lines = []

    for node_name, label in STAGES:
        if node_name in completed_nodes:
            lines.append(f"âœ… &nbsp; ~~{label}~~")
        elif node_name == current_node:
            lines.append(f"â³ &nbsp; **{label}** _(in progress...)_")
        else:
            lines.append(f"âšª &nbsp; {label}")

    container.markdown(
        "<div style='font-size:18px; line-height:2.1;'>"
        + "<br>".join(lines)
        + "</div>",
        unsafe_allow_html=True,
    )


def show_processing_page():
    st.markdown(
        "<h1 style='text-align:center;'>ðŸ¤– Analyzing Your Startup Idea</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#cbd5e1;'>"
        "Our multi-agent pipeline is researching your market, competitors, "
        "and risks in real time."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    idea = st.session_state.get("idea", {})
    startup_idea_text = idea.get("startup_idea_text", "")

    if not startup_idea_text:
        st.error("No startup idea found. Please go back and submit one.")
        if st.button("â† Back to Start"):
            st.session_state.page = "submit"
            st.rerun()
        return

    left, center, right = st.columns([1, 3, 1])

    with center:
        with st.container(border=True):
            progress_bar = st.progress(0)
            checklist_box = st.empty()
            status_line = st.empty()

    _render_checklist(checklist_box, set(), STAGES[0][0])

    initial_state = {"startup_idea": startup_idea_text}
    final_state = initial_state
    completed_nodes: set = set()

    # graph.stream() yields one update per node as the real pipeline
    # executes it, so the checklist reflects genuine agent progress
    # rather than a fixed sleep-based animation.
    try:
        for update in graph.stream(initial_state):
            node_name = next(iter(update))
            final_state = update[node_name]

            completed_nodes.add(node_name)
            progress_bar.progress(int((len(completed_nodes) / len(STAGES)) * 100))

            remaining = [n for n, _ in STAGES if n not in completed_nodes]
            next_node = remaining[0] if remaining else None
            _render_checklist(checklist_box, completed_nodes, next_node)

        errors = final_state.get("errors", [])
        if errors:
            status_line.warning(
                "âš ï¸ Completed with some agent errors: " + "; ".join(errors)
            )
            time.sleep(1.0)
        else:
            status_line.success("âœ… Validation complete!")
            time.sleep(0.8)

        st.session_state.validation_result = final_state

    except Exception as e:
        status_line.error(f"âŒ Pipeline failed: {e}")
        st.session_state.validation_result = {"errors": [str(e)]}
        time.sleep(1.5)

    st.session_state.page = "report"
    st.rerun()
