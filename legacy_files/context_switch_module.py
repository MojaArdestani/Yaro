import os
from dotenv import load_dotenv
import json
import openai
from openai import OpenAI
import os
import re


# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
# API_KEY = os.getenv('OPENAI_API_KEY')

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

client = OpenAI(
    api_key=api_key,
)

def if_move_to_next_question(chat_history, example_flow = os.path.join(os.path.dirname(__file__), "../Module 4 - Application/example_flow.json")):
    """
    Determines whether it is an appropriate moment in the conversation to ask the user if they want to move on to the next question.

    This function analyzes the current `chat_history` and compares it to an `example_flow` to infer conversational patterns, such as topic exploration depth, user satisfaction, and natural pauses. 
    For specific questions about success or gratitude, it ensures the conversation follows a four-step structure: ask, respond, inquire about impact, celebrate, and then prompt to move on.

    Args:
        chat_history (list or dict): The ongoing conversation history between the user and the AI.
        example_flow (str, optional): Path to a JSON file containing a sample conversation flow. Defaults to ".../Application/example_flow.json".

    Returns:
        int: Returns 1 if it is a good moment to ask about moving on to the next question, or 0 if not.
    """
    
    from .prompts import MOVE_TO_NEXT_QUESTION_PROMPT
    prompt_instructions = MOVE_TO_NEXT_QUESTION_PROMPT.format(
        chat_history=json.dumps(chat_history, indent=2),
        example_flow=json.dumps(example_flow, indent=2)
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        # temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_instructions}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "move_to_next_question_schema",
                "schema": {
                                "type": "object",
                                "properties": {
                                    "binary_value": {
                                        "type": "integer",
                                        "enum": [0, 1],
                                        "description": "0 or 1 indicating whether to move on"
                                    }
                                },
                                "required": ["binary_value"],
                                "additionalProperties": False
                            },
                "strict": True
        }
    })

    assistant_reply = response.choices[0].message.content
    print(assistant_reply)
    match = re.search(r'"binary_value"\s*:\s*(\d+)', assistant_reply)
    value = int(match.group(1))
    return value