import streamlit as st

# Custom imports aligned with your ui/ directory layout
from components.idea_input import show_idea_input
from components.processing_page import show_processing_page
from components.report_viewer import show_report
from components.advisor_page import show_advisor
from ui.chat_component import render_global_chat

st.set_page_config(
    page_title="AI Startup Idea Validator",
    page_icon="ðŸ¤–",
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
    margin-bottom: 24px;
}

.hero-badges {
    text-align: center;
    margin-bottom: 40px;
}

.hero-badge {
    display: inline-block;
    background: rgba(192, 132, 252, 0.12);
    border: 1px solid #581c87;
    color: #e9d5ff;
    border-radius: 999px;
    padding: 6px 16px;
    margin: 0 6px;
    font-size: 14px;
}

/* Feature cards on the landing page */
.feature-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid #2e1065;
    border-radius: 14px;
    padding: 20px;
    height: 100%;
}

.feature-card h4 {
    margin-top: 0;
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

.stButton > button:disabled {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #a1a1aa !important;
    border: 1px solid #3f3f46 !important;
    box-shadow: none !important;
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

/* Bordered containers used as cards throughout the app */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #2e1065 !important;
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 14px !important;
}

</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

# HOME PAGE
if st.session_state.page == "home":
    st.markdown('<div class="hero-title">ðŸ¤– AI Startup Idea Validator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Validate your startup idea with a multi-agent AI research pipeline - '
        'market sizing, competitor research, SWOT, MVP scope, and go-to-market, in minutes.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-badges">'
        '<span class="hero-badge">ðŸ”Ž Live Market Research</span>'
        '<span class="hero-badge">ðŸ¢ Competitor Analysis</span>'
        '<span class="hero-badge">ðŸ“Š SWOT & Risk</span>'
        '<span class="hero-badge">ðŸš€ GTM Strategy</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])
    with center:
        if st.button("âœ¨ Validate My Startup Idea", use_container_width=True, type="primary"):
            st.session_state.page = "submit"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("ðŸ”Ž", "Web Search Agent", "Gathers live market context and news for your idea."),
        ("ðŸ¢", "Competitor Agent", "Finds real, named competitors with strengths and weaknesses."),
        ("ðŸ“Š", "SWOT & Risk Agent", "Surfaces strengths, weaknesses, and execution risks."),
        ("ðŸš€", "GTM Agent", "Recommends positioning, channels, and a launch plan."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(
                f'<div class="feature-card"><h4>{icon} {title}</h4>'
                f'<p style="color:#d8b4fe; font-size:14px;">{desc}</p></div>',
                unsafe_allow_html=True,
            )

# SUBMIT IDEA PAGE
elif st.session_state.page == "submit":
    show_idea_input()

# PROCESSING PAGE
elif st.session_state.page == "processing":
    show_processing_page()

# REPORT PAGE
elif st.session_state.page == "report":
    show_report()

# CONVERSATIONAL ADVISOR PAGE
elif st.session_state.page == "advisor":
    show_advisor()

render_global_chat()
