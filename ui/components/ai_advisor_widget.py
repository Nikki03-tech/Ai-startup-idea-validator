""" Floating AI Advisor chat widget - compact edition.

Supports:
- General AI chat before validation
- Report-grounded chat after validation
- Persistent PostgreSQL-backed conversation history
- FastAPI /chat and /chat/history endpoints
- Floating bottom-right AI Advisor launcher
"""

import os
import uuid
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
_REQUEST_TIMEOUT = 30

_QUICK_START_SUGGESTIONS = [
    "Biggest competitors?",
    "How can I improve my MVP?",
    "What are the biggest risks?",
]


def _init_state():
    if "advisor_widget_open" not in st.session_state:
        st.session_state.advisor_widget_open = False

    if "advisor_widget_session_id" not in st.session_state:
        st.session_state.advisor_widget_session_id = str(uuid.uuid4())

    if "advisor_widget_conversation_id" not in st.session_state:
        st.session_state.advisor_widget_conversation_id = None

    if "advisor_widget_messages" not in st.session_state:
        st.session_state.advisor_widget_messages = []

    if "advisor_widget_error" not in st.session_state:
        st.session_state.advisor_widget_error = None

    if "advisor_widget_history_loaded_for" not in st.session_state:
        st.session_state.advisor_widget_history_loaded_for = None

    if "advisor_widget_show_suggestions" not in st.session_state:
        st.session_state.advisor_widget_show_suggestions = True


def _current_report() -> dict:
    final_state = st.session_state.get("validation_result", {}) or {}
    return final_state.get("report", {}) or {}


def _load_history(conversation_id: int):
    try:
        response = requests.get(
            f"{API_BASE_URL}/chat/history/{conversation_id}",
            timeout=_REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()

            st.session_state.advisor_widget_messages = [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in data.get("messages", [])
            ]

            st.session_state.advisor_widget_error = None

            if st.session_state.advisor_widget_messages:
                st.session_state.advisor_widget_show_suggestions = False

        else:
            st.session_state.advisor_widget_error = (
                "Couldn't load chat history."
            )

    except requests.exceptions.RequestException:
        st.session_state.advisor_widget_error = (
            "Can't reach the AI Advisor service right now."
        )

    st.session_state.advisor_widget_history_loaded_for = conversation_id


def _send_message(question: str):
    question = question.strip()

    if not question:
        return

    st.session_state.advisor_widget_show_suggestions = False
    st.session_state.advisor_widget_error = None

    report = _current_report()

    payload = {
        "question": question,
        "session_id": st.session_state.advisor_widget_session_id,
    }

    conversation_id = st.session_state.advisor_widget_conversation_id

    if conversation_id is not None:
        payload["conversation_id"] = conversation_id

    if report:
        payload["report"] = report

    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=_REQUEST_TIMEOUT,
        )

    except requests.exceptions.RequestException:
        st.session_state.advisor_widget_error = (
            "Can't reach the AI Advisor service right now. "
            "Please make sure FastAPI is running."
        )
        return

    if response.status_code == 200:
        data = response.json()

        st.session_state.advisor_widget_conversation_id = (
            data["conversation_id"]
        )

        st.session_state.advisor_widget_history_loaded_for = None

        st.session_state.advisor_widget_messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        st.session_state.advisor_widget_messages.append(
            {
                "role": "assistant",
                "content": data["answer"],
            }
        )

    else:
        try:
            detail = response.json().get("detail", "")
        except ValueError:
            detail = ""

        st.session_state.advisor_widget_error = (
            detail
            or "The AI Advisor couldn't respond. Please try again."
        )


def _handle_send(question: str, pending_slot):
    st.session_state.advisor_widget_show_suggestions = False

    with pending_slot.container():
        _render_pending_exchange(question)

    _send_message(question)

    pending_slot.empty()

    st.rerun()


def _inject_widget_css():

    st.markdown(
        """
        <style>

        /* =========================================================
           CLOSED AI ADVISOR LAUNCHER
           ========================================================= */

        .st-key-advisor_widget_button_wrap {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            z-index: 9999 !important;

            width: 70px !important;
            height: 70px !important;

            padding: 0 !important;
            margin: 0 !important;

            overflow: visible !important;
        }


        .st-key-advisor_widget_button_wrap .stButton {
            width: 70px !important;
            height: 70px !important;

            padding: 0 !important;
            margin: 0 !important;
        }


        /* Circular radiant launcher */

        .st-key-advisor_widget_button_wrap .stButton > button {

            width: 70px !important;
            height: 70px !important;

            min-width: 70px !important;
            min-height: 70px !important;

            max-width: 70px !important;
            max-height: 70px !important;

            padding: 0 !important;
            margin: 0 !important;

            border-radius: 50% !important;

            font-size: 0 !important;
            color: transparent !important;

            display: flex !important;
            align-items: center !important;
            justify-content: center !important;

            background: linear-gradient(
                135deg,
                #7e22ce 0%,
                #9333ea 50%,
                #a855f7 100%
            ) !important;

            border: 2px solid #c084fc !important;

            box-shadow:
                0 8px 30px rgba(147, 51, 234, 0.68),
                inset 0 0 16px rgba(255, 255, 255, 0.12) !important;

            position: relative !important;

            overflow: visible !important;

            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease !important;
        }


        /* Large white diamond ONLY for closed launcher */

        .st-key-advisor_widget_button_wrap .stButton > button::after {

            content: "âœ¦" !important;

            position: absolute !important;

            inset: 0 !important;

            display: flex !important;

            align-items: center !important;
            justify-content: center !important;

            font-size: 52px !important;

            line-height: 1 !important;

            color: white !important;

            font-weight: 400 !important;

            pointer-events: none !important;
        }


        .st-key-advisor_widget_button_wrap .stButton > button:hover {

            transform: scale(1.08) !important;

            box-shadow:
                0 12px 38px rgba(192, 132, 252, 0.85),
                inset 0 0 18px rgba(255, 255, 255, 0.18) !important;
        }


        .st-key-advisor_widget_button_wrap .stButton > button:active {

            transform: scale(0.95) !important;
        }


        /* =========================================================
           CHAT PANEL
           ========================================================= */

        .st-key-advisor_widget_panel {

            position: fixed !important;

            /* PANEL IS HIGHER THAN BEFORE */
            bottom: 135px !important;

            right: 20px !important;

            z-index: 9998 !important;

            width: 430px !important;

            max-width: calc(100vw - 30px) !important;

            background:
                linear-gradient(
                    160deg,
                    #120d1d 0%,
                    #09090b 100%
                ) !important;

            border: 1px solid #581c87 !important;

            border-radius: 20px !important;

            box-shadow:
                0 12px 45px rgba(0, 0, 0, 0.60),
                0 0 0 1px rgba(168, 85, 247, 0.08) !important;

            padding: 18px !important;

            overflow: visible !important;

            animation: advisor-panel-in 0.18s ease-out !important;
        }


        @keyframes advisor-panel-in {

            from {
                opacity: 0;
                transform: translateY(10px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }


        /* =========================================================
           HEADER
           ========================================================= */

        .advisor-widget-header {

            display: flex;
            align-items: center;
            justify-content: space-between;

            width: 100%;

            border-bottom: 1px solid #2e1065;

            padding: 2px 42px 12px 2px;

            margin-bottom: 10px;

            overflow: visible !important;
        }


        .advisor-widget-header-left {

            display: flex;
            align-items: center;

            gap: 10px;

            min-width: 0;
        }


        .advisor-widget-avatar-ring {

            width: 42px;
            height: 42px;

            border-radius: 50%;

            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            font-size: 22px;

            background:
                linear-gradient(
                    135deg,
                    #7e22ce 0%,
                    #a855f7 100%
                );

            box-shadow:
                0 0 0 2px rgba(192, 132, 252, 0.35);
        }


        .advisor-widget-title-block {

            display: flex;
            flex-direction: column;

            line-height: 1.2;

            min-width: 0;
        }


        .advisor-widget-title {

            font-weight: 700;

            font-size: 17px;

            white-space: nowrap;

            background:
                linear-gradient(
                    90deg,
                    #e9d5ff 0%,
                    #c084fc 50%,
                    #a855f7 100%
                );

            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }


        .advisor-widget-status {

            display: flex;
            align-items: center;

            gap: 5px;

            font-size: 11px;

            color: #d8b4fe;

            margin-top: 2px;
        }


        .advisor-status-dot {

            width: 6px;
            height: 6px;

            border-radius: 50%;

            background: #c084fc;

            box-shadow:
                0 0 6px 1px rgba(192, 132, 252, 0.8);

            animation:
                advisor-status-blink 1.8s ease-in-out infinite;
        }


        @keyframes advisor-status-blink {

            0%, 100% {
                opacity: 1;
            }

            50% {
                opacity: 0.35;
            }
        }


        /* =========================================================
           CLOSE BUTTON
           ========================================================= */

        .st-key-advisor_widget_minimize_btn {

            position: absolute !important;

            top: 12px !important;
            right: 12px !important;

            z-index: 20 !important;
        }


        .st-key-advisor_widget_minimize_btn .stButton > button {

            width: 30px !important;
            height: 30px !important;

            min-width: 30px !important;
            min-height: 30px !important;

            padding: 0 !important;
            margin: 0 !important;

            border-radius: 50% !important;

            border:
                1px solid rgba(192, 132, 252, 0.25) !important;

            background:
                rgba(168, 85, 247, 0.08) !important;

            color: #d8b4fe !important;

            font-size: 18px !important;

            font-weight: 700 !important;

            line-height: 1 !important;

            display: flex !important;

            align-items: center !important;
            justify-content: center !important;

            box-shadow: none !important;
        }


        .st-key-advisor_widget_minimize_btn .stButton > button:hover {

            background:
                rgba(168, 85, 247, 0.20) !important;

            border-color: #a855f7 !important;

            color: white !important;
        }


        /* =========================================================
           MESSAGES
           ========================================================= */

        .st-key-advisor_widget_messages {

            max-height: 380px;

            overflow-y: auto;

            padding-right: 5px;

            margin-bottom: 8px;
        }


        .advisor-msg-row {

            display: flex;

            align-items: flex-end;

            gap: 7px;

            margin: 10px 0;
        }


        .advisor-msg-row.user {
            justify-content: flex-end;
        }


        .advisor-msg-row.assistant {
            justify-content: flex-start;
        }


        .advisor-avatar {

            width: 25px;
            height: 25px;

            min-width: 25px;

            border-radius: 50%;

            display: flex;

            align-items: center;
            justify-content: center;

            font-size: 12px;

            color: white;
        }


        .advisor-avatar.assistant {

            background:
                linear-gradient(
                    135deg,
                    #7e22ce 0%,
                    #a855f7 100%
                );
        }


        .advisor-avatar.user {

            background:
                rgba(255, 255, 255, 0.10);

            border:
                1px solid #581c87;

            color: #e9d5ff;

            font-size: 10px;

            font-weight: 700;
        }


        .advisor-msg-bubble {

            max-width: 78%;

            padding: 9px 13px;

            border-radius: 13px;

            font-size: 13px;

            line-height: 1.45;

            word-wrap: break-word;
        }


        .advisor-msg-bubble.user {

            background:
                linear-gradient(
                    90deg,
                    #7e22ce 0%,
                    #9333ea 100%
                );

            color: #ffffff;

            border-bottom-right-radius: 3px;
        }


        .advisor-msg-bubble.assistant {

            background:
                rgba(255, 255, 255, 0.05);

            border:
                1px solid #2e1065;

            color: #f3e8ff;

            border-bottom-left-radius: 3px;
        }


        /* =========================================================
           TYPING INDICATOR
           ========================================================= */

        .advisor-typing-dots {

            display: inline-flex;

            align-items: center;

            gap: 3px;

            padding: 2px 0;
        }


        .advisor-typing-dots .dot {

            width: 6px;
            height: 6px;

            border-radius: 50%;

            background: #c084fc;

            animation:
                advisor-typing-bounce 1.2s infinite ease-in-out;
        }


        .advisor-typing-dots .dot:nth-child(1) {
            animation-delay: 0s;
        }

        .advisor-typing-dots .dot:nth-child(2) {
            animation-delay: 0.18s;
        }

        .advisor-typing-dots .dot:nth-child(3) {
            animation-delay: 0.36s;
        }


        @keyframes advisor-typing-bounce {

            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.5;
            }

            30% {
                transform: translateY(-4px);
                opacity: 1;
            }
        }


        /* =========================================================
           EMPTY STATE
           ========================================================= */

        .advisor-empty-state {

            display: flex;

            flex-direction: column;

            align-items: center;

            text-align: center;

            padding: 8px 6px 3px 6px;
        }


        .advisor-empty-avatar {

            width: 56px;
            height: 56px;

            border-radius: 50%;

            display: flex;

            align-items: center;
            justify-content: center;

            font-size: 28px;

            background:
                linear-gradient(
                    135deg,
                    #7e22ce 0%,
                    #a855f7 100%
                );

            box-shadow:
                0 0 0 3px rgba(192, 132, 252, 0.25);

            margin-bottom: 9px;
        }


        .advisor-empty-text {

            color: #e9d5ff;

            font-size: 13px;

            line-height: 1.5;

            margin-bottom: 11px;
        }


        /* =========================================================
           QUICK QUESTIONS
           ========================================================= */

        .advisor-quick-label {

            color: #d8b4fe;

            opacity: 0.75;

            font-size: 9px !important;

            text-transform: uppercase;

            letter-spacing: 0.04em;

            margin: 2px 0 4px 2px;
        }


        .st-key-advisor_widget_suggestions .stButton > button {

            background:
                rgba(168, 85, 247, 0.08) !important;

            border:
                1px solid #581c87 !important;

            color: #e9d5ff !important;

            border-radius: 999px !important;

            padding: 4px 9px !important;

            min-height: 28px !important;

            height: auto !important;

            text-align: left !important;

            box-shadow: none !important;

            white-space: normal !important;

            line-height: 1.2 !important;
        }


        /* Streamlit inner text */

        .st-key-advisor_widget_suggestions
        .stButton > button p {

            font-size: 11px !important;

            line-height: 1.2 !important;

            margin: 0 !important;
        }


        .st-key-advisor_widget_suggestions
        .stButton > button div {

            font-size: 11px !important;

            line-height: 1.2 !important;
        }


        .st-key-advisor_widget_suggestions
        .stButton > button:hover {

            background:
                rgba(168, 85, 247, 0.20) !important;

            border-color: #a855f7 !important;

            color: #ffffff !important;
        }


        /* =========================================================
           CHAT INPUT
           ========================================================= */

        .st-key-advisor_widget_panel
        [data-testid="stChatInput"] {

            margin-top: 5px !important;
        }


        /* =========================================================
           MOBILE
           ========================================================= */

        @media (max-width: 600px) {

            .st-key-advisor_widget_panel {

                right: 15px !important;

                bottom: 120px !important;

                width: calc(100vw - 30px) !important;

                padding: 15px !important;
            }


            .st-key-advisor_widget_button_wrap {

                right: 20px !important;

                bottom: 20px !important;

                width: 60px !important;

                height: 60px !important;
            }


            .st-key-advisor_widget_button_wrap .stButton {

                width: 60px !important;

                height: 60px !important;
            }


            .st-key-advisor_widget_button_wrap
            .stButton > button {

                width: 60px !important;

                height: 60px !important;

                min-width: 60px !important;

                min-height: 60px !important;

                max-width: 60px !important;

                max-height: 60px !important;
            }


            .st-key-advisor_widget_button_wrap
            .stButton > button::after {

                font-size: 44px !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def _message_row_html(role: str, content: str) -> str:

    avatar = (
        '<div class="advisor-avatar assistant">âœ¦</div>'
        if role == "assistant"
        else '<div class="advisor-avatar user">You</div>'
    )

    if role == "assistant":

        return (
            '<div class="advisor-msg-row assistant">'
            f"{avatar}"
            '<div class="advisor-msg-bubble assistant">'
            f"{content}"
            "</div>"
            "</div>"
        )

    return (
        '<div class="advisor-msg-row user">'
        '<div class="advisor-msg-bubble user">'
        f"{content}"
        "</div>"
        f"{avatar}"
        "</div>"
    )


def _typing_indicator_html() -> str:

    return (
        '<div class="advisor-msg-row assistant">'
        '<div class="advisor-avatar assistant">âœ¦</div>'
        '<div class="advisor-msg-bubble assistant">'
        '<span class="advisor-typing-dots">'
        '<span class="dot"></span>'
        '<span class="dot"></span>'
        '<span class="dot"></span>'
        "</span>"
        "</div>"
        "</div>"
    )


def _render_pending_exchange(question: str):

    st.markdown(
        _message_row_html("user", question)
        + _typing_indicator_html(),
        unsafe_allow_html=True,
    )


def _render_quick_start():

    st.markdown(
        '<p class="advisor-quick-label">Quick questions</p>',
        unsafe_allow_html=True,
    )

    with st.container(key="advisor_widget_suggestions"):

        for i, suggestion in enumerate(_QUICK_START_SUGGESTIONS):

            if st.button(
                suggestion,
                key=f"advisor_widget_suggestion_{i}",
                use_container_width=True,
            ):

                st.session_state.advisor_widget_show_suggestions = False

                pending_slot = st.empty()

                _handle_send(
                    suggestion,
                    pending_slot,
                )


def _render_messages():

    with st.container(key="advisor_widget_messages"):

        if not st.session_state.advisor_widget_messages:

            st.markdown(
                '<div class="advisor-empty-state">'
                '<div class="advisor-empty-avatar">âœ¦</div>'
                '<p class="advisor-empty-text">'
                "Hi! I'm your AI Advisor.<br>"
                "Ask me anything about your startup idea, "
                "strategy, MVP, market, or validation."
                "</p>"
                "</div>",
                unsafe_allow_html=True,
            )

            if st.session_state.advisor_widget_show_suggestions:
                _render_quick_start()

        else:

            html_parts = [
                _message_row_html(
                    "user"
                    if message["role"] == "user"
                    else "assistant",
                    message["content"],
                )
                for message
                in st.session_state.advisor_widget_messages
            ]

            st.markdown(
                "".join(html_parts),
                unsafe_allow_html=True,
            )


def show_ai_advisor_widget():

    _init_state()

    _inject_widget_css()

    conversation_id = (
        st.session_state.advisor_widget_conversation_id
    )

    if (
        conversation_id is not None
        and
        st.session_state.advisor_widget_history_loaded_for
        != conversation_id
    ):

        _load_history(conversation_id)


    #OPEN CHAT PANEL

    if st.session_state.advisor_widget_open:

        with st.container(
            key="advisor_widget_panel"
        ):

            st.markdown(
                '<div class="advisor-widget-header">'
                '<div class="advisor-widget-header-left">'
                '<div class="advisor-widget-avatar-ring">âœ¦</div>'
                '<div class="advisor-widget-title-block">'
                '<span class="advisor-widget-title">'
                "AI Advisor"
                "</span>"
                '<span class="advisor-widget-status">'
                '<span class="advisor-status-dot"></span>'
                "Online"
                "</span>"
                "</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )


            if st.button(
                "Ã—",
                key="advisor_widget_minimize_btn",
                help="Close AI Advisor",
            ):

                st.session_state.advisor_widget_open = False

                st.rerun()


            _render_messages()

            pending_slot = st.empty()


            if st.session_state.advisor_widget_error:

                st.error(
                    st.session_state.advisor_widget_error
                )


            question = st.chat_input(
                "Type your message...",
                key="advisor_widget_chat_input",
            )


            if question:

                st.session_state.advisor_widget_show_suggestions = False

                _handle_send(
                    question,
                    pending_slot,
                )


    else:

        #CLOSED LAUNCHER 

        with st.container(
            key="advisor_widget_button_wrap"
        ):

            if st.button(
                "âœ¦",
                key="advisor_widget_toggle_btn",
                help="Open AI Advisor",
            ):

                st.session_state.advisor_widget_open = True

                st.rerun()
