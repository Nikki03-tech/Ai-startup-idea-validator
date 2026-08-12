import streamlit as st

def show_idea_input():
    st.markdown("<h1 style='text-align:center;'>💡 Submit Your Startup Idea</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#cbd5e1;'>Tell us about your startup and let AI validate it.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        startup_name = st.text_input("🚀 Startup Name", placeholder="e.g. AI Idea Validator")
        industry = st.selectbox(
            "🏢 Industry",
            ["AI", "FinTech", "Healthcare", "EdTech", "E-Commerce", "Cybersecurity", "Other"]
        )

    with col2:
        target_audience = st.text_input("🎯 Target Audience", placeholder="e.g. Founders, Investors")
        business_model = st.selectbox(
            "💼 Business Model",
            ["B2B", "B2C", "Subscription", "Marketplace", "Freemium"]
        )

    problem = st.text_area(
        "❓ Problem Statement",
        height=120,
        placeholder="What core problem are you solving?"
    )

    solution = st.text_area(
        "🛠️ Proposed Solution",
        height=120,
        placeholder="How does your startup solve this problem?"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📊 Analyze Startup Idea", use_container_width=True):
        if not startup_name or not problem or not solution:
            st.warning("Please fill in at least the Startup Name, Problem, and Solution.")
        else:
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