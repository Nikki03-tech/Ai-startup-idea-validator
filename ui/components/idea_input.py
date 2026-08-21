import streamlit as st


INDUSTRY_OPTIONS = [
    "AI / Machine Learning",
    "FinTech",
    "Healthcare",
    "EdTech",
    "E-Commerce",
    "Agriculture / AgriTech",
    "Cybersecurity",
    "SaaS / Enterprise Software",
    "Climate / CleanTech",
    "Other",
]


def _derive_title(idea_text: str) -> str:
    """
    Build a short, human-friendly title for headers/report display from
    the free-text startup idea, since the backend's StartupIdea model
    doesn't have a dedicated "name" field and we're not inventing one.
    """

    if not idea_text:
        return "Your Startup"

    words = idea_text.strip().split()
    title = " ".join(words[:8])

    if len(words) > 8:
        title += "..."

    return title


def show_idea_input():
    st.markdown(
        "<h1 style='text-align:center;'>ðŸ’¡ Tell Us About Your Startup</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#d8b4fe;'>"
        "A few clear details help our multi-agent pipeline research the "
        "right market, the right competitors, and the right risks."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("idea_input_form", border=False):
        with st.container(border=True):
            st.markdown("#### ðŸš€ Startup Idea")
            idea = st.text_area(
                "Describe your startup idea",
                placeholder=(
                    "e.g. An AI-powered platform that helps students prepare "
                    "for technical interviews with personalized mock "
                    "interviews and instant feedback."
                ),
                height=90,
                label_visibility="collapsed",
                help="A short, clear summary of what you're building.",
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ðŸŽ¯ Target Audience")
                target_audience = st.text_input(
                    "Target audience",
                    placeholder="e.g. College students preparing for placements",
                    label_visibility="collapsed",
                    help="Who is this startup built for?",
                )

            with col2:
                st.markdown("#### ðŸ¢ Industry")
                industry = st.selectbox(
                    "Industry",
                    INDUSTRY_OPTIONS,
                    label_visibility="collapsed",
                    help="Pick the closest match - this gives the agents useful context.",
                )

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### â“ Problem Statement")
            problem = st.text_area(
                "Problem statement",
                placeholder="What core problem are you solving, and for whom?",
                height=110,
                label_visibility="collapsed",
                help="Be specific about the pain point - this drives the market and SWOT research.",
            )

            st.markdown("#### ðŸ› ï¸ Proposed Solution")
            solution = st.text_area(
                "Proposed solution",
                placeholder="How does your product or service solve that problem?",
                height=110,
                label_visibility="collapsed",
                help="Describe the approach, not just the feature list.",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        left, col_submit, col_back = st.columns([2, 2, 1])

        with col_back:
            back_clicked = st.form_submit_button(
                "â† Back", use_container_width=True
            )

        with col_submit:
            submit_clicked = st.form_submit_button(
                "ðŸ“Š Validate My Startup Idea", use_container_width=True, type="primary"
            )

    if back_clicked:
        st.session_state.page = "home"
        st.rerun()

    if submit_clicked:
        missing = [
            label
            for label, value in [
                ("Startup Idea", idea),
                ("Target Audience", target_audience),
                ("Problem Statement", problem),
                ("Proposed Solution", solution),
            ]
            if not (value or "").strip()
        ]

        if missing:
            st.warning(
                "Please fill in the following before continuing: "
                + ", ".join(missing)
            )
        else:
            # pipeline/graph.py's GraphState expects a single
            # "startup_idea" string - combine the structured form
            # fields into one description for the agents to work from.
            # This mirrors the backend's existing input contract and
            # does not change it.
            startup_idea_text = (
                f"{idea.strip()} "
                f"(Industry: {industry}) "
                f"Problem: {problem.strip()} "
                f"Solution: {solution.strip()} "
                f"Target audience: {target_audience.strip()}"
            )

            st.session_state.idea = {
                "idea": idea.strip(),
                "target_audience": target_audience.strip(),
                "industry": industry,
                "problem": problem.strip(),
                "solution": solution.strip(),
                "startup_idea_text": startup_idea_text,
                "display_title": _derive_title(idea.strip()),
            }
            st.session_state.page = "processing"
            st.rerun()
