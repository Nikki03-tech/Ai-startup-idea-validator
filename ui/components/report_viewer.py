import streamlit as st

def show_report():
    report = st.session_state.get("report", {})
    idea = st.session_state.get("idea", {})

    st.markdown(f"<h1>📈 Validation Report: {idea.get('startup_name', 'Startup')}</h1>", unsafe_allow_html=True)
    st.divider()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Validation Score", f"{report.get('score', 'N/A')}/100")
    with m2:
        st.metric("Market Potential", report.get("market_potential", "N/A"))
    with m3:
        st.metric("Risk Level", report.get("risk_level", "N/A"))

    st.divider()

    st.markdown("### 📊 SWOT Analysis")
    swot = report.get("swot", {})
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Strengths**\n{swot.get('strengths', 'N/A')}")
        st.markdown(f"**Opportunities**\n{swot.get('opportunities', 'N/A')}")
    with col2:
        st.markdown(f"**Weaknesses**\n{swot.get('weaknesses', 'N/A')}")
        st.markdown(f"**Threats**\n{swot.get('threats', 'N/A')}")

    st.divider()

    st.markdown("### 💡 MVP Recommendation")
    st.write(report.get("mvp_recommendation", "N/A"))

    st.markdown("### 🚀 Go-To-Market Strategy")
    st.write(report.get("gtm_strategy", "N/A"))

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Validate Another Idea", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()