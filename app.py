"""
This is a Streamlit-based conversational coaching chatbot application that guides users
through structured conversations with intelligent follow-ups using LangChain and GPT models.
"""

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from chat_controller import (
    initialize_session_state,
    setup_initial_question
)
from UI_utils import (
    setup_streamlit_page,
    render_chat_history,
    render_input_field,
    render_end_conversation_button,
    MSG_CONVERSATION_ENDED_INFO
)


def initialize_llm():
    """Initialize and return the LLM instance."""
    load_dotenv()
    return ChatOpenAI(model="gpt-4", temperature=0.0)

def main():
    """Main application function."""
    # Initialize LLM
    llm = initialize_llm()

    # Set up the Streamlit page
    setup_streamlit_page()
    initialize_session_state()
    
    # Setup initial question if needed
    setup_initial_question()
    
    # Display chat history (uses st.chat_message which auto-scrolls)
    render_chat_history(llm)
    
    # Render input field and buttons
    if st.session_state.conversation_active:
        render_input_field(llm)
    else:
        st.info(MSG_CONVERSATION_ENDED_INFO)
    
    # Render end conversation button
    render_end_conversation_button(llm)

if __name__ == "__main__":
    main()
