"""
A bit more advanced sequence:
1. Check if email was supplied
2. If yes, note down an email and ask for more questions
Otherwise:
3. Query VDB
4. Answer based on that info

* Also keeps the conversation memory, last 8 messages

https://python.langchain.com/docs/use_cases/question_answering/chat_vector_db
"""

import os
import sys

from langchain.output_parsers import BooleanOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableBranch
from langchain_community.chat_models import ChatOpenAI

from bots.chain_s1 import final_chain
from bots.librarian import librarian_agent

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)


def is_data_entry(message):
    llm = ChatOpenAI(
        temperature=0,
        model=app_settings.GPT_35,
    )

    prompt = PromptTemplate.from_template("Check if the user wants to add some info to the knowledge base."
                                          "Answer YES or NO.\n"
                                          "User message:{message}")
    runnable = prompt | llm | BooleanOutputParser()
    return runnable.invoke({"message": message})


counselor_chain = RunnableBranch(
    (is_data_entry, librarian_agent()),
    final_chain
)

if __name__ == '__main__':
    while True:
        user_input = input('>>> ')
        response = counselor_chain.invoke(user_input)
        print(response)
