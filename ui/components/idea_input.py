import streamlit as st

def show_idea_input():

    st.title("💡 Submit Startup Idea")

    startup_name = st.text_input("Startup Name")

    industry = st.selectbox(
        "Industry",
        ["AI", "Healthcare", "FinTech", "Education", "E-commerce"]
    )

    idea = st.text_area(
        "Describe your startup idea",
        height=200
    )

    if st.button("🤖 Analyze Idea"):

        st.session_state.startup_name = startup_name
        st.session_state.industry = industry
        st.session_state.idea = idea

        st.session_state.page = "report"
        st.rerun()
