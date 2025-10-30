"""
Simple terminal version of the chat application for testing and debugging purposes.
"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from chains import (
    run_follow_up_chain, 
    run_summary_chain, 
    run_move_to_next_chain,
    run_follow_up_chain_raw,
    run_move_to_next_chain_raw
)

def initialize_llm():
    """Initialize and return the LLM instance."""
    load_dotenv()
    return ChatOpenAI(model="gpt-4", temperature=0.0)

# Initialize global variables
chat_history = []
chat_history_for_flag = []
basic_questions = [
    "What is one success you had today?",
    "What is one struggle you had today?",
    "What one thing you are grateful for today?",
    "What are one or two things that stood out to you today?"
]
transition_question = "That's great. Do you want to move on to the next question?"
current_question_index = 0

def process_user_input(user_input, llm):
    """Process user input and generate bot response."""
    print("\n> Your message:", user_input)
    
    # Add user input to histories
    chat_history.append({"role": "user", "content": user_input})
    chat_history_for_flag.append({"role": "user", "content": user_input})

    # Check if we're responding to a transition question
    last_bot_message = next(
        (msg["content"] for msg in reversed(chat_history[:-1]) 
         if msg["role"] == "bot"),
        None
    )

    if last_bot_message == transition_question:
        handle_transition_response(user_input, llm)
    else:
        handle_normal_response(llm)

def handle_transition_response(user_input, llm):
    """Handle user's response to transition question."""
    global current_question_index
    
    if user_input.lower() in ["yes", "y"]:
        # Clear flag history and move to next question
        chat_history_for_flag.clear()
        next_question = basic_questions[current_question_index]
        current_question_index += 1
        
        # Add bot response
        chat_history.append({"role": "bot", "content": next_question})
        print("\n> Bot:", next_question)
    else:
        # Continue current conversation
        print("\n=== RAW LLM OUTPUT ===")
        raw_output = run_follow_up_chain_raw(chat_history, llm)
        print(raw_output)
        print("=====================")
        
        # Get parsed response
        bot_reply = run_follow_up_chain(chat_history, llm)
        print("\n=== PARSED OUTPUT ===")
        print(bot_reply)
        print("=====================")
        
        # Add bot response
        chat_history.append({"role": "bot", "content": bot_reply})
        print("\n> Bot:", bot_reply)

def handle_normal_response(llm):
    """Handle normal conversation flow."""
    # Check for transition
    example_flow_path = os.path.join(os.path.dirname(__file__), "example_flow.json")
    
    print("\n=== TRANSITION CHECK RAW ===")
    raw_transition = run_move_to_next_chain_raw(chat_history_for_flag, example_flow_path, llm)
    print(raw_transition)
    print("===========================")
    
    should_transition = run_move_to_next_chain(chat_history_for_flag, example_flow_path, llm)
    print("\n=== TRANSITION DECISION ===")
    print("Result:", should_transition)
    print("===========================")

    if should_transition != 1:
        # Get follow-up question
        print("\n=== FOLLOW-UP RAW ===")
        raw_followup = run_follow_up_chain_raw(chat_history, llm)
        print(raw_followup)
        print("====================")
        
        bot_reply = run_follow_up_chain(chat_history, llm)
        print("\n=== FOLLOW-UP PARSED ===")
        print(bot_reply)
        print("=======================")
        
        # Add bot response
        chat_history.append({"role": "bot", "content": bot_reply})
        print("\n> Bot:", bot_reply)
    else:
        # Show transition question
        chat_history.append({"role": "bot", "content": transition_question})
        print("\n> Bot:", transition_question)

def save_summary(llm):
    """Generate and save conversation summary."""
    print("\nGenerating conversation summary...")
    chat_summary = run_summary_chain(chat_history, llm)
    
    with open("chat_history_summary.json", "w") as f:
        json.dump(chat_summary, f, indent=2)
    print("Summary saved to 'chat_history_summary.json'")

def main():
    """Main chat loop."""
    llm = initialize_llm()
    
    print("\nWelcome to the Terminal Chat!")
    print("Type 'quit' to end the conversation")
    
    # Display first question
    first_question = basic_questions[0]
    chat_history.append({"role": "bot", "content": first_question})
    print("\n> Bot:", first_question)
    global current_question_index
    current_question_index = 1

    while True:
        user_input = input("\nYour message: ").strip()
        if user_input.lower() == 'quit':
            save_summary(llm)
            print("\nGoodbye!")
            break
        
        process_user_input(user_input, llm)

if __name__ == "__main__":
    main()