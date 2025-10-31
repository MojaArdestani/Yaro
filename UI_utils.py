"""
UI Rendering Module - Frontend Layer
Pure rendering functions with no business logic.
All logic is handled in chat_controller.py
"""

import streamlit as st
from chat_controller import (
    process_user_input, process_yes_no_response,
    generate_assistant_response, end_conversation,
    TRANSITION_QUESTION, QUESTIONS, ROLE_ASSISTANT, ROLE_USER
)

# UI Configuration
APP_TITLE = "Chatbot Interface"
APP_ICON = "🤖"

# UI-only constants
BTN_YES_LABEL = "✅ Yes"
BTN_NO_LABEL = "❌ No"

# Status messages (UI display only)
STATUS_THINKING = "Thinking..."
STATUS_PROCESSING = "Processing your message..."
STATUS_COMPLETE = "Complete!"
MSG_CONVERSATION_ENDED_INFO = "The conversation has ended. Refresh the page to start a new chat."
INPUT_PLACEHOLDER = "Your message:"
BTN_END_CONVERSATION = "End Conversation"

# CSS Color scheme
COLOR_GREEN = "#28a745"
COLOR_GREEN_HOVER = "#218838"
COLOR_GREEN_BORDER = "#1e7e34"
COLOR_RED = "#dc3545"
COLOR_RED_HOVER = "#c82333"
COLOR_RED_BORDER = "#bd2130"
COLOR_WHITE = "white"


def setup_streamlit_page():
    """Configure Streamlit page settings and styling."""
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON)
    
    # Custom CSS for Yes/No buttons using centralized color constants
    st.markdown(f"""
        <style>
        /* Style for buttons in general */
        div[data-testid="stHorizontalBlock"] button {{
            width: 100%;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }}
        
        /* Yes button styling - overriding primary type */
        div[data-testid="stHorizontalBlock"] button[kind="primary"] {{
            background-color: {COLOR_GREEN} !important;
            color: {COLOR_WHITE} !important;
            border: 2px solid {COLOR_GREEN} !important;
        }}
        
        div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {{
            background-color: {COLOR_GREEN_HOVER} !important;
            border-color: {COLOR_GREEN_BORDER} !important;
            transform: scale(1.02);
        }}
        
        /* No button styling - default secondary type */
        div[data-testid="stHorizontalBlock"] button[kind="secondary"] {{
            background-color: {COLOR_RED} !important;
            color: {COLOR_WHITE} !important;
            border: 2px solid {COLOR_RED} !important;
        }}
        
        div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {{
            background-color: {COLOR_RED_HOVER} !important;
            border-color: {COLOR_RED_BORDER} !important;
            transform: scale(1.02);
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.title(f"{APP_ICON} {APP_TITLE}")

def render_input_field(llm):
    """Render the chat input field for user messages (UI only)."""
    user_input = st.chat_input(INPUT_PLACEHOLDER)
    process_user_input(user_input, llm)

def render_end_conversation_button(llm):
    """Render the end conversation button (UI only)."""
    if st.button(BTN_END_CONVERSATION):
        end_conversation(llm)

def render_chat_history(llm):
    """Display the entire chat history (UI rendering only)."""
    chat_history = st.session_state.chat_history
    history_len = len(chat_history)
    
    # Render all messages
    for idx, message in enumerate(chat_history):
        is_last_message = (idx == history_len - 1)
        render_single_message(message, is_last_message, llm)
        
    # Check if last message is from user and needs a response
    if (st.session_state.conversation_active and 
        chat_history and 
        chat_history[-1]["role"] == ROLE_USER):
        render_thinking_and_generate_response(llm)

def render_single_message(message: dict, is_last_message: bool, llm):
    """Render a single chat message with appropriate styling and buttons."""
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Show Yes/No buttons only for the last assistant message if it's a question
        if (is_last_message and 
            st.session_state.conversation_active and
            message["role"] == ROLE_ASSISTANT and
            (message["content"] == TRANSITION_QUESTION or message["content"] == QUESTIONS[-1])):
            render_yes_no_buttons(llm)

def render_yes_no_buttons(llm):
    """Render Yes and No buttons side by side (UI only)."""
    chat_history_len = len(st.session_state.chat_history)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(BTN_YES_LABEL, key=f"yes_btn_{chat_history_len}", type="primary"):
            process_yes_no_response("yes")
    with col2:
        if st.button(BTN_NO_LABEL, key=f"no_btn_{chat_history_len}"):
            process_yes_no_response("no")

def render_thinking_and_generate_response(llm):
    """Render thinking indicator and generate response (UI rendering)."""
    with st.chat_message(ROLE_ASSISTANT):
        with st.status(STATUS_THINKING, expanded=True) as status:
            st.write(STATUS_PROCESSING)
            
            # Get the user's last message and generate response
            user_input = st.session_state.chat_history[-1]["content"]
            generate_assistant_response(user_input, llm)
            
            status.update(label=STATUS_COMPLETE, state="complete", expanded=False)
    
    # Rerun to display the new assistant message (only if still active)
    if st.session_state.conversation_active:
        st.rerun()