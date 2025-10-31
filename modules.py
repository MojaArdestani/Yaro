import json
from langchain_core.prompts import PromptTemplate
from prompts import FOLLOW_UP_QUESTION_PROMPT, SUMMARIZE_CHAT_HISTORY_PROMPT, MOVE_TO_NEXT_QUESTION_PROMPT
from outputparsers import FollowUpQuestionParser, ChatSummaryParser, MoveToNextQuestionParser


def run_follow_up_chain(chat_history, llm):
    prompt = PromptTemplate(
        input_variables=["chat_history"],
        template=FOLLOW_UP_QUESTION_PROMPT
    )
    parser = FollowUpQuestionParser()
    chain = prompt | llm | parser
    return chain.invoke({"chat_history": json.dumps(chat_history, indent=2)})

def run_summary_chain(chat_history, llm):
    prompt = PromptTemplate(
        input_variables=["chat_history"],
        template=SUMMARIZE_CHAT_HISTORY_PROMPT
    )
    parser = ChatSummaryParser()
    chain = prompt | llm | parser
    return chain.invoke({"chat_history": json.dumps(chat_history, indent=2)})

def run_move_to_next_chain(chat_history, example_flow, llm):
    prompt = PromptTemplate(
        input_variables=["chat_history", "example_flow"],
        template=MOVE_TO_NEXT_QUESTION_PROMPT
    )
    parser = MoveToNextQuestionParser()
    chain = prompt | llm | parser
    return chain.invoke({
        "chat_history": json.dumps(chat_history, indent=2),
        "example_flow": json.dumps(example_flow, indent=2)
    })
