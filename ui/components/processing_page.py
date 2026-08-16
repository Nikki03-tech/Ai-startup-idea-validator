import streamlit as st
from app.orchestrator import run_analysis

def show_processing_page():
    st.markdown("<h1 style='text-align:center;'>🤖 AI Processing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#d8b4fe;'>Running autonomous AI agents to validate your startup...</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    idea_data = st.session_state.get("idea", {})

    with st.spinner("🤖 AI Agents are actively researching market trends, competitors, and risks..."):
        try:
            ai_results = run_analysis(idea_data)
            st.session_state.report = ai_results

            st.success("✅ Analysis completed successfully!")
            
            st.session_state.page = "report"
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Error running AI pipeline: {str(e)}")
            if st.button("⬅️ Go Back to Form"):
                st.session_state.page = "submit"
                st.rerun()