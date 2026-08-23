import streamlit as st
from agents.conversational_advisor import ConversationalAdvisor


def _get_advisor() -> ConversationalAdvisor:
    """Reuse a single ConversationalAdvisor instance across reruns."""
    if "advisor_instance" not in st.session_state:
        st.session_state.advisor_instance = ConversationalAdvisor()
    return st.session_state.advisor_instance


def show_advisor():
    """Renders the AI Copilot floating popover pinned at the bottom-center of the screen."""

    # Fixed CSS that anchors Streamlit's Popover container to the bottom center
    st.markdown(
        """
        <style>
        /* Anchor the popover wrapper to bottom center */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 25px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 999999 !important;
        }

        /* Style the AI Copilot trigger button */
        div[data-testid="stPopover"] > button {
            background-color: #1e1b4b !important;
            border: 1px solid #818cf8 !important;
            color: #f3e8ff !important;
            border-radius: 20px !important;
            padding: 8px 24px !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            box-shadow: 0px 4px 20px rgba(129, 140, 248, 0.4) !important;
        }

        div[data-testid="stPopover"] > button:hover {
            background-color: #312e81 !important;
            border-color: #c084fc !important;
            box-shadow: 0px 0px 25px rgba(192, 132, 252, 0.6) !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Floating Popover Modal
    with st.popover("🤖 AI Copilot", help="Click to open AI Assistant"):
        st.markdown("### Startup Copilot")
        st.caption("Persistent context across all pages")
        st.markdown("---")

        final_state = st.session_state.get("validation_result", {}) or {}
        report = final_state.get("report", {}) or {}

        if "advisor_history" not in st.session_state:
            st.session_state.advisor_history = [
                {
                    "question": None,
                    "answer": (
                        "👋 Hi! I'm your AI Copilot. Ask me anything about your"
                        " startup validation report or market strategy."
                    ),
                }
            ]

        # Render conversation history inside popover view
        for entry in st.session_state.advisor_history:
            if entry["question"]:
                with st.chat_message("user"):
                    st.write(entry["question"])
            if entry["answer"]:
                with st.chat_message("assistant"):
                    st.write(entry["answer"])

        # Input box inside the popover
        question = st.chat_input("Ask a question...")

        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                if not report:
                    fallback_ans = (
                        "Hello! How can I assist you today? Tell me a bit"
                        " about your startup idea, or run a validation first"
                        " so I can answer questions grounded in your report."
                    )
                    st.write(fallback_ans)
                    st.session_state.advisor_history.append(
                        {"question": question, "answer": fallback_ans}
                    )
                else:
                    with st.spinner("Thinking..."):
                        advisor = _get_advisor()
                        result = advisor.answer_question(report, question)

                    if result.get("status") == "success":
                        answer = result.get("answer", "")
                        st.write(answer)
                        st.session_state.advisor_history.append(
                            {"question": question, "answer": answer}
                        )
                    else:
                        error_msg = (
                            result.get("message") or "Something went wrong."
                        )
                        st.error(error_msg)