import streamlit as st
from app.orchestrator import answer_chat_question

def render_global_chat():
    """Renders a fixed, floating AI chat popover accessible across all pages."""
    
    # 1. Initialize persistent chat state in Streamlit session memory
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "👋 Hi! I'm your AI Copilot. Ask me anything about your startup validation report or market strategy."}
        ]

    # 2. Inject CSS to float the Popover button at the bottom-right of the screen
    st.markdown(
        """
        <style>
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 25px !important;
            right: 25px !important;
            z-index: 999999 !important;
        }
        div[data-testid="stPopover"] > button {
            border-radius: 50px !important;
            background-color: #7C3AED !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(0,0,0,0.3) !important;
            padding: 12px 24px !important;
            font-weight: bold !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 3. Render Floating Popover Chat Window
    with st.popover("💬 AI Copilot", help="Click to open AI Assistant"):
        st.subheader("Startup Copilot")
        st.caption("Persistent context across all pages")

        chat_container = st.container(height=350)

        # Render conversation history
        with chat_container:
            for message in st.session_state["chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Handle user text input
        if user_input := st.chat_input("Ask a question..."):
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        ai_response = answer_chat_question(
                            chat_history=st.session_state["chat_history"],
                            current_prompt=user_input,
                        )
                        st.markdown(ai_response)

            # Save assistant response to session state and refresh UI
            st.session_state["chat_history"].append({"role": "assistant", "content": ai_response})
            st.rerun()
