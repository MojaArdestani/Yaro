from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import json

def clean_text(text):
    """Simple text cleanup."""
    if hasattr(text, 'content'):
        text = text.content
    text = text.strip()
    if text.startswith('```') and text.endswith('```'):
        text = '\n'.join(text.split('\n')[1:-1])
    return text

class FollowUpQuestionParser(StrOutputParser):
    def parse(self, text):
        text = clean_text(text)
        try:
            # Try as JSON first
            data = json.loads(text)
            return str(data.get('question', text))
        except:
            # If not JSON, return cleaned text
            return text

class ChatSummaryParser(StrOutputParser):
    def parse(self, text):
        text = clean_text(text)
        try:
            # Try as JSON first
            data = json.loads(text)
            return {
                'Goals': data.get('Goals', []),
                'Follow_Up_Opportunities': data.get('Follow_Up_Opportunities', [])
            }
        except:
            # If not JSON, return default structure
            return {
                'Goals': ['Unable to parse summary'],
                'Follow_Up_Opportunities': ['Unable to parse summary']
            }

class MoveToNextQuestionParser(StrOutputParser):
    def parse(self, text):
        text = clean_text(text)
        try:
            # Try as JSON first
            data = json.loads(text)
            if isinstance(data, dict):
                return 1 if data.get('binary_value', 0) == 1 else 0
            # Handle direct number
            return 1 if int(str(data)) == 1 else 0
        except:
            # For non-JSON input
            return 1 if text.strip() in ['1', 'true', 'True'] else 0
