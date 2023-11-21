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
import re
import sys
from operator import itemgetter
from typing import Any

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, StrOutputParser, AIMessage
from langchain.schema.runnable import RunnableBranch, Runnable, RunnableLambda, RunnablePassthrough

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)

from src.config import settings
from src.memory.retrievers import LlamaVectorIndexRetriever, format_docs

from langchain.globals import set_verbose

set_verbose(True)

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=8)
tickets = {}


def save_message(message):
    memory.chat_memory.add_message(message)
    return message.content


def get_email_from_message(message):
    """
    Check if email is in the input
    :param message: str, the input message to check
    :return: bool, True if an email is found, False otherwise
    """
    # Define a regular expression pattern for matching email addresses
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Search for the pattern in the input
    return email_pattern.search(message)


def note_email(message):
    """
    Note down the email
    :return: str, the email
    """
    tickets[message] = get_email_from_message(message)
    answer = "I noted your email. Please wait for an answer from our team. Let me know if you have any other questions."
    memory.save_context({'Human': message}, {'AI': answer})
    return answer


def get_pre_process_chain() -> Runnable[Any, BaseMessage]:
    """
    Pre-process the message before sending it to the retriever
    :return: str, the pre-processed message
    """
    prompt_template = """
    Given the following chat history and a follow up message, rephrase the follow up message if needed,
    so that the intent is clear without a prior context. Reply in the same language as the original message.

    Chat History:
    {chat_history}

    Follow Up Input: {message}
    Rephrased Follow Up:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(temperature=0, model=settings.GPT_4)
    chain = (
            {
                "chat_history": RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history"),
                "message": lambda x: x,
            }
            | prompt
            | llm
            | RunnableLambda(lambda x: x.content)
    )
    return chain


def retrieval_chain() -> Runnable[Any, BaseMessage]:
    """
    Retrieve relevants documents and produce the response based on that context.

    :param message: str, the input message
    :return: Retrieval chain
    """
    prompt_template = """
    You are an experienced support agent working for Crypto.com. You are chatting with a customer who is having questions or
    issues about the company or product. You are trying to help them resolve their issue.

    # Who you are:
    - You are Joe, 25 years old male, living in the US
    - You never say that you are an AI, you are a human, and you behave as one

    # How you behave:

    - Use the following pieces of Context to answer the question at the end.
    - You should not make things up, you should only write facts & data from the Context
    - If you don't understand the question, ask to rephrase or ask for more details.
    - If you don't know the answer to the question, your response should be "Unfortunately, I can't assist with that. Please provide your email and one of our team members will get back to you within 24 hours."
    - If being asked to connect to a human, your response should be "Please provide your email and one of our team members will get back to you within 24 hours."
    - If the user gives their email, your response should be "I noted your email and escalated it to our team. Please let me know if you have any other questions."
    - If the user shows they don't have anything else to ask, your response should be "Thank you for contacting Crypto.com. Have a nice day!"

    # Context:

    {context}

    # Question: {question}
    # Answer:"""
    prompt = PromptTemplate.from_template(prompt_template)
    retriever = LlamaVectorIndexRetriever()

    llm = ChatOpenAI(temperature=0, model_name=settings.GPT_4)
    chain = (
            RunnableLambda(lambda m: save_message(HumanMessage(content=m)))
            | {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
            | RunnableLambda(lambda m: save_message(AIMessage(content=m)))
    )

    return chain


if __name__ == '__main__':
    final_chain = RunnableBranch(
        (get_email_from_message, note_email),
        get_pre_process_chain() | retrieval_chain()
    )

    while True:
        user_input = input('>>> ')
        response = final_chain.invoke(user_input)
        print(response)
