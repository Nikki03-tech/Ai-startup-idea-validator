import streamlit as st

def show_idea_input():

    st.markdown("""
    <h1 style='text-align:center;'>💡 Submit Your Startup Idea</h1>
    <p style='text-align:center;color:gray;'>
    Tell us about your startup and let AI validate it.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        startup_name = st.text_input("🚀 Startup Name")
        industry = st.selectbox(
            "🏢 Industry",
            [
                "AI",
                "FinTech",
                "Healthcare",
                "EdTech",
                "E-Commerce",
                "Cybersecurity",
                "Other"
            ]
        )

    with col2:
        target_audience = st.text_input("🎯 Target Audience")
        business_model = st.selectbox(
            "💰 Business Model",
            [
                "B2B",
                "B2C",
                "Subscription",
                "Marketplace",
                "Freemium"
            ]
        )

    problem = st.text_area(
        "❗ Problem Statement",
        height=150
    )

    solution = st.text_area(
        "💡 Proposed Solution",
        height=150
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🤖 Analyze Startup Idea", use_container_width=True):

        st.session_state.idea = {
            "startup_name": startup_name,
            "industry": industry,
            "target_audience": target_audience,
            "business_model": business_model,
            "problem": problem,
            "solution": solution
        }

        st.session_state.page = "processing"
        st.rerun()