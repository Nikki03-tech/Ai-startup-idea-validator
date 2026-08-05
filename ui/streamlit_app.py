import streamlit as st
from components.idea_input import show_idea_input
from components.report_viewer import show_report

st.set_page_config(
    page_title="AI Startup Idea Validator",
    page_icon="🚀",
    layout="wide"
)

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":

    st.title("🚀 AI Startup Idea Validator")

    st.subheader("Validate your startup idea using Multi-Agent AI")

    st.write("Get market analysis, competitor research, risks, MVP roadmap and GTM strategy.")

    if st.button("🚀 Start Validation"):
        st.session_state.page = "submit"
        st.rerun()

elif st.session_state.page == "submit":
    show_idea_input()

elif st.session_state.page == "report":
    show_report()
