"""
This is a Streamlit-based conversational coaching chatbot application that guides users
through structured conversations with intelligent follow-ups using LangChain and GPT models.
"""

from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from utils import (
    setup_streamlit_page,
    initialize_session_state,
    render_chat_history,
    setup_initial_question,
    render_input_field,
    render_end_conversation_button
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
    
    # Display chat history
    render_chat_history()
    
    # Render input field if conversation is active
    if st.session_state.conversation_active:
        render_input_field(llm)
    else:
        st.info("The conversation has ended. Refresh the page to start a new chat.")
    
    # Render end conversation button
    render_end_conversation_button(llm)

if __name__ == "__main__":
    main()
