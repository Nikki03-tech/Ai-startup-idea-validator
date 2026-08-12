import streamlit as st
import time

def show_processing_page():
    st.markdown("<h1 style='text-align:center;'>🤖 AI Processing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#cbd5e1;'>Analyzing your startup idea using multi-agent workflow...</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_box = st.empty()

    agents = [
        "Market Research Agent",
        "Competitor Analysis Agent",
        "Risk Assessment Agent",
        "SWOT Analysis Agent",
        "MVP Recommendation Agent",
        "GTM Strategy Agent",
        "Revenue Model Agent",
        "Report Generation Agent"
    ]

    for i, agent in enumerate(agents):
        status_box.info(f"⏳ **Executing:** {agent}...")
        progress_bar.progress(int(((i + 1) / len(agents)) * 100))
        time.sleep(0.8)

    status_box.success("✅ Processing complete!")
    time.sleep(1.2)

    st.session_state.page = "report"
    st.rerun()