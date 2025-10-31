"""
Chat Controller - Business Logic Layer
Handles all conversation logic, state management, and response generation.
Separated from UI rendering for clean architecture.
"""

import os
import json
import streamlit as st
from modules import run_follow_up_chain, run_summary_chain, run_move_to_next_chain

# Constants needed for business logic
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"

AFFIRMATIVE_RESPONSES = {"yes", "y"}

QUESTIONS = [
    "What is one success you had today?",
    "What is one struggle you had today?",
    "What one thing you are grateful for today?",
    "What are one or two things that stood out to you today?",
    "Great, I have asked all of my questions! Is there anything else that you want to talk about with me?"
]
TRANSITION_QUESTION = "That's great. Do you want to move on to the next question?"

MSG_LISTENING = "Go ahead, I'm listening."
MSG_FAREWELL = "Thank you for sharing. Saving our conversation..."
MSG_CONVERSATION_ENDED = "Conversation ended."

CHAT_SUMMARY_FILE = "chat_history_summary.json"
EXAMPLE_FLOW_FILE = "example_flow.json"

########################################################
# chat Initialization Functions
########################################################
def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history_for_flag = []
        st.session_state.question_index = 0

    if "conversation_active" not in st.session_state:
        st.session_state.conversation_active = True


def setup_initial_question():
    """Set up the first question if starting a new conversation."""
    if not st.session_state.chat_history:
        first_question = get_next_reflection_question()
        add_message_to_history(ROLE_ASSISTANT, first_question)


def get_next_reflection_question() -> str:
    """Get the next question from the list."""
    if st.session_state.question_index < len(QUESTIONS):
        question = QUESTIONS[st.session_state.question_index]
        st.session_state.question_index += 1
        return question
    return None


def add_message_to_history(role: str, content: str, update_flag: bool = True):
    """
    Add a message to chat history.
    
    Args:
        role: The role of the message sender (user or assistant)
        content: The message content
        update_flag: Whether to also update the flag history for transition detection
    """
    message = {"role": role, "content": content}
    st.session_state.chat_history.append(message)
    
    if update_flag:
        st.session_state.chat_history_for_flag.append(message)

########################################################
# Chat Follow Up Functions
########################################################
def get_last_assistant_message(exclude_last: bool = False) -> str:
    """Get the last assistant message from chat history."""
    chat_history = st.session_state.chat_history
    history = chat_history[:-1] if exclude_last and chat_history else chat_history
    for msg in reversed(history):
        if msg["role"] == ROLE_ASSISTANT:
            return msg["content"]
    return None


def generate_assistant_response(user_input: str, llm):
    """Generate assistant response based on user input (user message already in history)."""
    last_assistant_msg = get_last_assistant_message(exclude_last=True)
    
    # Handle final question response (last question in the list)
    if last_assistant_msg == QUESTIONS[-1]:
        handle_final_question_response(user_input, llm)
        return
    
    # Handle transition response
    if last_assistant_msg == TRANSITION_QUESTION:
        handle_transition_response(user_input, llm)
        return
    
    # Regular conversation - check if we should transition
    handle_regular_response(llm)


def handle_final_question_response(user_input: str, llm):
    """Handle user response to the final question."""
    if user_input.lower() in AFFIRMATIVE_RESPONSES:
        # User wants to add more
        st.session_state.chat_history_for_flag = []
        add_message_to_history(ROLE_ASSISTANT, MSG_LISTENING)
    else:
        # User is done, end conversation
        add_message_to_history(ROLE_ASSISTANT, MSG_FAREWELL)
        end_conversation(llm)


def handle_transition_response(user_input: str, llm):
    """Handle user response to transition question."""
    if user_input.lower() in AFFIRMATIVE_RESPONSES:
        # Move to next question
        st.session_state.chat_history_for_flag = []
        next_question = get_next_reflection_question()
        if next_question:
            add_message_to_history(ROLE_ASSISTANT, next_question)
    else:
        # Continue with follow-up on current topic
        bot_reply = run_follow_up_chain(st.session_state.chat_history, llm)
        add_message_to_history(ROLE_ASSISTANT, bot_reply)


def handle_regular_response(llm):
    """Handle regular conversation and check for transition."""
    example_flow_path = os.path.join(os.path.dirname(__file__), EXAMPLE_FLOW_FILE)
    should_transition = run_move_to_next_chain(
        st.session_state.chat_history_for_flag, 
        example_flow_path, 
        llm
    ) == 1
    
    if should_transition:
        # Ask transition question or move to next question
        add_message_to_history(ROLE_ASSISTANT, TRANSITION_QUESTION)
    else:
        # Continue with follow-up question
        bot_reply = run_follow_up_chain(st.session_state.chat_history, llm)
        add_message_to_history(ROLE_ASSISTANT, bot_reply)


def end_conversation(llm):
    """Handle conversation termination and summary generation."""
    st.session_state.conversation_active = False
    
    chat_summary = run_summary_chain(st.session_state.chat_history, llm)
    save_chat_summary(chat_summary)
    st.success(MSG_CONVERSATION_ENDED)


def save_chat_summary(chat_summary: dict):
    """Save the chat summary to a JSON file."""
    with open(CHAT_SUMMARY_FILE, "w") as f:
        json.dump(chat_summary, f, indent=2)


def process_user_input(user_input: str, llm):
    """Process user input and trigger response generation."""
    if user_input and user_input.strip():
        add_message_to_history(ROLE_USER, user_input.strip())
        st.rerun()


def process_yes_no_response(response: str):
    """Process Yes/No button response - adds message, response generation handled in UI."""
    add_message_to_history(ROLE_USER, response)
    st.rerun()

