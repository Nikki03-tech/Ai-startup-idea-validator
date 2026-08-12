import streamlit as st

# Custom imports aligned with your ui/ directory layout
from ui.components.idea_input import show_idea_input
from ui.components.processing_page import show_processing_page
from ui.components.report_viewer import show_report

st.set_page_config(
    page_title="AI Startup Idea Validator",
    layout="wide"
)

# Dark theme styling override
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}

h1, h2, h3, h4, label, .stMarkdown p {
    color: #f0f6fc !important;
}

.hero-title {
    text-align: center;
    font-size: 56px;
    font-weight: 800;
    color: #ffffff;
    margin-top: 50px;
}

.hero-subtitle {
    text-align: center;
    font-size: 20px;
    color: #8b949e;
    margin-bottom: 40px;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

# HOME PAGE
if st.session_state.page == "home":
    st.markdown('<div class="hero-title">🤖 AI Startup Idea Validator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Validate your startup idea using multi-agent AI workflow</div>', unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])
    with center:
        if st.button("Start Validation", use_container_width=True):
            st.session_state.page = "submit"
            st.rerun()

# SUBMIT IDEA PAGE
elif st.session_state.page == "submit":
    show_idea_input()

# PROCESSING PAGE
elif st.session_state.page == "processing":
    show_processing_page()

# REPORT PAGE
elif st.session_state.page == "report":
    show_report()