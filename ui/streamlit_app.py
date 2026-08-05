import streamlit as st
from components.idea_input import show_idea_input
from components.report_viewer import show_report
from components.processing_page import show_processing_page

st.set_page_config(
    page_title="AI Startup Idea Validator",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stApp{
    background: linear-gradient(
        135deg,
        #020617 0%,
        #0f172a 50%,
        #111827 100%
    );
}

.main-title{
    text-align:center;
    font-size:90px;
    font-weight:800;
    color:white;
    margin-top:80px;
}

.subtitle{
    text-align:center;
    font-size:30px;
    color:#cbd5e1;
    margin-top:20px;
    margin-bottom:40px;
}

.metric-box{
    text-align:center;
    color:white;
    padding:20px;
}

.metric-number{
    font-size:48px;
    font-weight:700;
}

.metric-label{
    font-size:18px;
    color:#94a3b8;
}

</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

# HOME PAGE
if st.session_state.page == "home":

    st.markdown("""
    <div class="main-title">
        🚀 AI Startup Idea Validator
    </div>

    <div class="subtitle">
        Validate your startup idea in minutes using AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-number">1250+</div>
            <div class="metric-label">Ideas Validated</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-number">8</div>
            <div class="metric-label">AI Agents</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-number">5000+</div>
            <div class="metric-label">Reports Generated</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    left, center, right = st.columns([1,2,1])

    with center:
        if st.button("🚀 Start Validation", use_container_width=True):
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