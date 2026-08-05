import streamlit as st

def show_report():

    idea = st.session_state.get("idea", {})

    st.title("📊 Validation Report")

    st.subheader(idea.get("startup_name", "Startup"))

    st.success("Idea Validation Completed")

    st.metric("Validation Score", "87/100")

    st.metric("Market Potential", "High")

    st.metric("Risk Level", "Medium")

    st.markdown("## SWOT Analysis")

    st.write("""
    **Strengths**
    - Innovative concept
    - Growing market

    **Weaknesses**
    - Requires funding

    **Opportunities**
    - Global scalability

    **Threats**
    - Existing competitors
    """)

    st.markdown("## MVP Recommendation")

    st.write("""
    Build a basic prototype focusing on core features.
    """)

    st.markdown("## Go-To-Market Strategy")

    st.write("""
    Start with early adopters and digital marketing.
    """)

    if st.button("🔄 Validate Another Idea"):
        st.session_state.page = "home"
        st.rerun()