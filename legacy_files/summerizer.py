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

# Line 46 does not make sense to me.
def summerize_chat_history(chat_history):
    """Summarizes a chat history between a human and an AI bot, focusing on self-improvement goals and follow-up opportunities.

    Args:
        chat_history (list or dict): The conversation history to be summarized.

    Returns:
        dict: A dictionary containing two keys:
            - "Goals": A list of goals set or implied by the human for self-improvement.
            - "Follow_Up_Opportunities": A list (maximum 2) of follow-up opportunities for future progress.

    Notes:
        - The summary ignores the bot's content unless it adds important context to the human's responses.
        - The output is structured and concise, returned in JSON format."""
    
    from .prompts import SUMMARIZE_CHAT_HISTORY_PROMPT
    prompt_instructions = SUMMARIZE_CHAT_HISTORY_PROMPT.format(chat_history=json.dumps(chat_history, indent=2))

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_instructions}
        ],
        response_format= {"type": "json_schema", "json_schema":{
                                                                "name": "conversation_summary",
                                                                "schema": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                    "Goals": {
                                                                        "type": "array",
                                                                        "description": "List of goals set or implied by the human for self-improvement.",
                                                                        "items": {
                                                                        "type": "string"
                                                                        }
                                                                    },
                                                                    "Follow_Up_Opportunities": {
                                                                        "type": "array",
                                                                        "description": "List of follow-up opportunities that a coach or assistant could use to support future progress.",
                                                                        "items": {
                                                                        "type": "string"
                                                                        }
                                                                    }
                                                                    },
                                                                    "required": [
                                                                    "Goals",
                                                                    "Follow_Up_Opportunities"
                                                                    ],
                                                                    "additionalProperties": False
                                                                },
                                                                "strict": True
                                                                }
                                                                })

    assistant_reply = response.choices[0].message.content
    output = json.loads(assistant_reply)
    print(output)
    return output 