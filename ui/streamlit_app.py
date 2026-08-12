import streamlit as st

# Custom imports aligned with your ui/ directory layout
from ui.components.idea_input import show_idea_input
from ui.components.processing_page import show_processing_page
from ui.components.report_viewer import show_report

st.set_page_config(
    page_title="AI Startup Idea Validator",
    page_icon="🤖",
    layout="wide"
)

# Dark Black & Lavender Aesthetic Styling
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Deep Dark Background */
.stApp {
    background: linear-gradient(135deg, #09090b 0%, #120d1d 50%, #050508 100%) !important;
    color: #f3e8ff !important;
}

/* Headings and Text in Soft Lavender/White */
h1, h2, h3, h4, label, .stMarkdown p {
    color: #f3e8ff !important;
}

/* Hero Section Lavender Highlights */
.hero-title {
    text-align: center;
    font-size: 56px;
    font-weight: 800;
    background: linear-gradient(90deg, #e9d5ff 0%, #c084fc 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 40px;
}

.hero-subtitle {
    text-align: center;
    font-size: 20px;
    color: #d8b4fe !important;
    margin-bottom: 40px;
}

/* Buttons with Lavender Accents */
.stButton > button {
    background: linear-gradient(90deg, #7e22ce 0%, #9333ea 100%) !important;
    color: #ffffff !important;
    border: 1px solid #c084fc !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #9333ea 0%, #a855f7 100%) !important;
    box-shadow: 0px 0px 15px rgba(192, 132, 252, 0.4) !important;
}

/* Input Fields - Dark Slate with Soft Lavender Borders */
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] {
    background-color: #18181b !important;
    color: #f3e8ff !important;
    border: 1px solid #581c87 !important;
    border-radius: 8px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #c084fc !important;
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