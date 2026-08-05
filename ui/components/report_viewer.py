import streamlit as st

def show_report():

    st.title("📊 Startup Validation Report")

    st.metric("Validation Score", "87/100")

    st.success("""
    Strong market opportunity with moderate competition.
    Recommended to build MVP and validate with early users.
    """)

    st.subheader("📈 Market Opportunity")
    st.write("High Growth Potential")

    st.subheader("🏆 Competition")
    st.write("Moderate")

    st.subheader("🚀 Recommendation")
    st.write("Proceed with MVP Development")

    if st.button("⬅ Back Home"):
        st.session_state.page = "home"
        st.rerun()
