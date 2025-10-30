import os
import json
import streamlit as st

from chains import run_move_to_next_chain, get_bot_response, run_summary_chain



def handle_conversation_end(llm):
    """Handle the end of conversation and generate summary."""
    # Mark conversation as inactive
    st.session_state.conversation_active = False
    
    # Add any remaining user input to chat history
    if st.session_state.user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": st.session_state.user_input})
    
    # Generate summary of the entire conversation using LangChain chain
    chat_summary = run_summary_chain(st.session_state.chat_history, llm)
    
    # Save the conversation summary to a JSON file for future reference
    with open("chat_history_summary.json", "w") as f:
        json.dump(chat_summary, f, indent=2)
    
    st.success("Conversation ended.")