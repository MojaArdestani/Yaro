# Conversational Coaching Chatbot

A Streamlit-based conversational coaching chatbot that guides users through structured conversations with intelligent follow-ups using LangChain and GPT models.

## Features

- Interactive chat interface with Streamlit
- Intelligent follow-up questions based on user responses
- Structured conversation flow with transition management
- Chat history summarization
- Support for basic questions and follow-up chains

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

## Modules Overview

### context_switch_module
A function that passes the current chat history and an example of chat flow (one-shot demonstration) to an LLM. The LLM decides whether it's a good time to switch the conversation to a new topic (returning 1 in JSON format) or should generate a follow-up question (returning 0).

**Consideration:** Currently, all reflection questions are generated based on order only and are not utilized from "Goals" list in previous sessions' summary.

### follow_up_question_module 
A function that passes the current chat history to an LLM, which generates an intelligent follow-up question and returns this question in JSON format.

**Consideration:** Currently, all follow-up questions are generated based on the current chat history only and are not utilized from "Follow_Up_Opportunities".

### summerizer
A function that passes the current chat history to an LLM, which generates two distinct outputs:
- **"Goals"**: A list of goals set or implied by the human for self-improvement.
- **"Follow_Up_Opportunities"**: A list (maximum 2) of follow-up opportunities for future progress.

### Application (app.py)
Initializes a Streamlit application that:
1. Starts a chat with a reflecting question
2. Updates the chat history based on user responses
3. Checks for follow-up generation or topic transition
4. Summarizes the chat history at the end

## Project Structure

- `app.py`: Main Streamlit application
- `chains.py`: LangChain conversation chains implementation
- `outputparsers.py`: Custom output parsers for LLM responses
- `prompts.py`: Prompt templates for different conversation scenarios
- `utils.py`: Utility functions for Streamlit UI and conversation management
- `example_flow.json`: Example conversation flow for reference


