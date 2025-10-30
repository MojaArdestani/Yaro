import os
from dotenv import load_dotenv
import json
import openai
from openai import OpenAI
import os
import re


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    api_key=API_KEY,
)

def ask_follow_up_question(chat_history):

    """Generates an insightful follow-up question based on the provided chat history, following specific conversational guidelines."""
    from .prompts import FOLLOW_UP_QUESTION_PROMPT
    prompt_instructions = FOLLOW_UP_QUESTION_PROMPT.format(chat_history=json.dumps(chat_history, indent=2))

    response = client.chat.completions.create(
        model="gpt-4o",
        # temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_instructions}
        ],
        response_format= {
            "type": "json_schema", 
            "json_schema":{
                "name": "my_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                    "question": {
                        "type": "string",
                        "description": "Follow up questions besed on the chat history."
                    }
                    },
                    "required": [
                    "question"
                    ],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )  

    assistant_reply = response.choices[0].message.content
    match = re.search(r'"question":\s*"(.*?)"', assistant_reply)
    question = match.group(1)
    #structured_questions = [{"Question": q} for q in questions]\

    return question