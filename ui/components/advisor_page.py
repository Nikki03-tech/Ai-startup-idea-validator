import streamlit as st

from agents.conversational_advisor import ConversationalAdvisor


def _get_advisor() -> ConversationalAdvisor:
    """
    Reuse a single ConversationalAdvisor instance across reruns instead
    of rebuilding the underlying Gemini client on every question -
    this is purely a Streamlit-side caching concern and does not
    change the backend agent itself.
    """

    if "advisor_instance" not in st.session_state:
        st.session_state.advisor_instance = ConversationalAdvisor()

    return st.session_state.advisor_instance


def show_advisor():
    st.markdown(
        "<h1 style='text-align:center;'>ðŸ’¬ Ask About Your Report</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#cbd5e1;'>"
        "Ask follow-up questions - answers are grounded in your actual "
        "validation report."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    final_state = st.session_state.get("validation_result", {}) or {}
    report = final_state.get("report", {}) or {}

    if not report:
        st.warning("No validation report available yet. Run a validation first.")
        if st.button("â† Back to Report"):
            st.session_state.page = "report"
            st.rerun()
        return

    if "advisor_history" not in st.session_state:
        st.session_state.advisor_history = []

    left, center, right = st.columns([1, 3, 1])

    with center:
        for entry in st.session_state.advisor_history:
            with st.chat_message("user"):
                st.write(entry["question"])
            with st.chat_message("assistant"):
                st.write(entry["answer"])

        question = st.chat_input("Ask a question about your validation report...")

        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
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
                    error_message = result.get("message") or "Something went wrong."
                    st.error(error_message)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("â† Back to Report", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()
