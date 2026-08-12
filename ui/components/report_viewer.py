import streamlit as st

def show_report():
    idea = st.session_state.get("idea", {})

    st.markdown(f"<h1>📈 Validation Report: {idea.get('startup_name', 'Startup')}</h1>", unsafe_allow_html=True)
    st.success("Validation completed successfully!")

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Validation Score", "87/100")
    with m2:
        st.metric("Market Potential", "High")
    with m3:
        st.metric("Risk Level", "Medium")

    st.divider()

    st.markdown("### 📊 SWOT Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Strengths**\n- High market demand\n- Scalable architecture")
        st.markdown("**Opportunities**\n- Rapid AI adoption\n- Global expansion potential")
    with col2:
        st.markdown("**Weaknesses**\n- Initial customer acquisition cost")
        st.markdown("**Threats**\n- Competitors entering the space")

    st.divider()

    st.markdown("### 💡 MVP Recommendation")
    st.write("Build a lightweight web app focusing on core validation tools before expanding the feature set.")

    st.markdown("### 🚀 Go-To-Market Strategy")
    st.write("Target early-stage founders via developer communities, incubators, and direct outreach.")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Validate Another Idea", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()