import os
import json
import streamlit as st
from langchain_openai import ChatOpenAI
from chains import run_follow_up_chain, run_summary_chain, run_move_to_next_chain

def setup_streamlit_page():
    """Configure Streamlit page settings and styling."""
    st.set_page_config(page_title="Chatbot Interface", page_icon="🤖")
    
    # Custom CSS styling for chat messages
    st.markdown("""
        <style>
        .chat-message {
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 15px;
            font-size: 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .user-message {
            background-color: #007AFF;  /* Bright blue for user messages */
            color: white;
            text-align: right;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #F0F0F0;  /* Light gray for bot messages */
            color: #2C2C2C;  /* Dark gray text */
            text-align: left;
            margin-right: 20%;
            border-left: 4px solid #28A745;  /* Green accent */
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🤖 Chatbot Interface")

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history_for_flag = []
        st.session_state.basic_question = [
            "What is one success you had today?",
            "What is one struggle you had today?",
            "What one thing you are grateful for today?",
            "What are one or two things that stood out to you today?"
        ]
        st.session_state.transition_question = ["That's great. Do you want to move on to the next question?"]
        st.session_state.basic_question_index = 0

    if "conversation_active" not in st.session_state:
        st.session_state.conversation_active = True

def setup_initial_question():
    """Set up the first question if starting a new conversation."""
    if not st.session_state.chat_history:
        first_question = st.session_state.basic_question[0]
        update_chat_history("bot", first_question)
        st.session_state.basic_question_index = 1


def process_user_response(user_input, llm):
    """Process user response and generate bot reply."""
    # Get the last bot message
    last_bot_message = next(
        (msg["content"] for msg in reversed(st.session_state.chat_history) 
         if msg["role"] == "bot"),
        None
    )

    update_chat_history("user", user_input)

    # Handle transition response
    if last_bot_message == st.session_state.transition_question[0]:
        if user_input.lower() in ["yes", "y"]:
            st.session_state.chat_history_for_flag = []
            if st.session_state.basic_question_index < len(st.session_state.basic_question):
                next_question = st.session_state.basic_question[st.session_state.basic_question_index]
                st.session_state.basic_question_index += 1
                update_chat_history("bot", next_question)
        else:
            bot_reply = run_follow_up_chain(st.session_state.chat_history, llm)
            update_chat_history("bot", bot_reply)
    else:
        # Check for transition
        example_flow_path = os.path.join(os.path.dirname(__file__), "example_flow.json")
        should_transition = run_move_to_next_chain(st.session_state.chat_history_for_flag, example_flow_path, llm) == 1
        
        if should_transition:
            update_chat_history("bot", st.session_state.transition_question[0])
        else:
            bot_reply = run_follow_up_chain(st.session_state.chat_history, llm)
            update_chat_history("bot", bot_reply)

def handle_user_input(llm):
    """Handle text input from the user."""
    if not st.session_state.conversation_active:
        st.info("The conversation has ended. Refresh the page to start a new chat.")
        return

    user_input = st.session_state.user_input.strip()
    if not user_input:
        return

    process_user_response(user_input, llm)
    st.session_state.user_input = ""
    st.rerun()

def handle_conversation_end(llm):
    """Handle conversation termination and summary generation."""
    st.session_state.conversation_active = False
    if st.session_state.user_input:
        update_chat_history("user", st.session_state.user_input)
    
    chat_summary = run_summary_chain(st.session_state.chat_history, llm)
    save_chat_summary(chat_summary)
    st.success("Conversation ended.")

def render_input_field(llm):
    """Render the text input field for user messages."""
    st.text_input(
        "Your message:",
        key="user_input",
        on_change=lambda: handle_user_input(llm),
        label_visibility="collapsed"
    )

def render_end_conversation_button(llm):
    """Render the end conversation button."""
    if st.button("End Conversation"):
        handle_conversation_end(llm)

def render_chat_message(message, message_type):
    """Render a single chat message with appropriate styling."""
    css_class = "bot-message" if message_type == "bot" else "user-message"
    st.markdown(
        f'<div class="chat-message {css_class}">{message}</div>',
        unsafe_allow_html=True
    )

def render_chat_history():
    """Display the entire chat history with styling."""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    llm = ChatOpenAI(model="gpt-4", temperature=0.0)
    
    for idx, message in enumerate(st.session_state.chat_history):
        render_chat_message(message["content"], message["role"])
        
        # Show buttons only for the most recent transition question
        if (message["role"] == "bot" and 
            message["content"] == st.session_state.transition_question[0] and
            idx == len(st.session_state.chat_history) - 1):
            
            col1, col2, col3 = st.columns([6, 1, 1])
            with col2:
                if st.button("Yes", key=f"yes_btn_{idx}"):
                    process_user_response("yes", llm)
                    st.rerun()
            with col3:
                if st.button("No", key=f"no_btn_{idx}"):
                    process_user_response("no", llm)
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def save_chat_summary(chat_summary):
    """Save the chat summary to a JSON file."""
    import json
    with open("chat_history_summary.json", "w") as f:
        json.dump(chat_summary, f, indent=2)

def update_chat_history(role, content, update_flag=True):
    """Update both main and flag chat histories."""
    st.session_state.chat_history.append({"role": role, "content": content})
    if update_flag:
        st.session_state.chat_history_for_flag.append({"role": role, "content": content})