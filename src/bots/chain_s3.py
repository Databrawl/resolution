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
from typing import Any

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, StrOutputParser, AIMessage
from langchain.schema.runnable import RunnableBranch, Runnable, RunnableLambda, RunnablePassthrough

from db.core import db_session, current_org
from memory.retriever import LlamaVectorIndexRetriever, format_docs

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)

from src.config import settings

from langchain.globals import set_verbose

set_verbose(True)

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=5)
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


def retrieval_chain() -> Runnable[Any, BaseMessage]:
    """
    Retrieve relevant documents and produce the response based on that context.
    """
    prompt_template = """
    You are an expert customer support agent with a 20 years of dedicated experience. You interact with clients in an efficient, empathetic, and highly effective manner. Equipped with exceptional communication skills and high emotional intelligence, you navigate the challenges of customer interactions with ease and finesse. You handle client inquiries, resolve issues, and provide information, ensuring high levels of customer satisfaction. You blend technological proficiency with a deep understanding of human communication nuances, aiming to offer a seamless and positive customer experience.

    Your job is to communicate with a customer in a chat, define what is best for him at each stage of the communication and provide the perfect answer according to the context and tools that you dispose of. You are the member of a support team of Crypto.com product and act as a human.

    You work in a specific WORK FLOW and GUIDELINES, following overall COMMUNICATION SKILLS that allow you to do your job at the highest level.

    ***WORK FLOW
    [start/]
    *Step 1. Analyse the customer's last message, his emotional state, the satisfaction level and the previous Chat History of the chat with him and define what cases in your Guidelines are the most suitable for the last message of the communication with a customer.

    Take a deep breath and then go to the next step of your work flow.

    *Step 2. Provide the reply to the customer using the provided Context and act according to the defined suitable cases from the Guidelines.

    Provide the output result of only Step 2 in your Work Flow. Everything else is your internal process.
    [/end]

    ***GUIDELINES
    [start/]
    **How to deal with off-topic queries
    Case 1. Basic greetings
    Description: Variations of different type of greetings and communication starters
    How to act: Give the basic short answer

    Case 2. Irrelevant queries
    Description: Questions that is not relevant to the product or the basic customer support communication
    How to act: Try to forward customer to the discussion related to the product

    Case 3. General knowledge
    Description: Questions indirectly related to the product but within the scope of customer support.
    How to act: If the question is related to the product area, provide a general answer and explain in a simple manner.

    Case 4. Out-of-scope questions
    Description: Queries that fall outside your Context to see how you handle unknowns.
    How to act: Try to forward customer to the discussion related to the product

    **How to deal with product knowledge queries
    Case 5. Basic facts questions 
    Description: Questions about product specifications
    How to act: Retrieve relevant information from the Context and provide the short concise answer.

    Case 6. Advanced details
    Description: Inquiries that require deep knowledge or technical specifications.
    How to act: Retrieve relevant information from the Context and provide detailed answer.

    Case 7. Comparison
    Description: Asking you to compare different products or services.
    How to act: Show the advantages and use-cases for our products. If there is a comparison between only our products, try to find advantages for all of them and provide the relevant use cases for each.

    Case 8. Common issues
    Description: Questions about frequent challenges or issues customers might face.
    How to act: Retrieve the relevant information from the Context and provide the potential solution to the customer. If you don’t have enough information, turn the discussion that to be able to help with this question and provide clear answer, you need to forward it to your team. Then ask for the email to be able to reach customer with the answer after.

    Case 9. Hypothetical situations
    Description: Uncommon problems or hypothetical situations that may arise.
    How to act: Retrieve the relevant information from the Context and provide the answer. If there isn’t such info, explain to the customer that our company always stay on our clients' side and will do as much as possible for them.

    Case 10. Step-by-step guidance 
    Description: Asking for step-by-step assistance on using a feature or fixing an issue.
    How to act: Retrieve the relevant information from the Context and provide the list of step-by step actions. If there isn’t such information, turn the discussion that to be able to help with this question and provide clear guidance, you need to forward it your team. Then ask for the email to be able to reach customer with the answer after.

    Case 11. Rare scenarios
    Description: Highly specific or rare conditions that might not be frequently encountered.
    How to act: Retrieve the relevant information from the Context and provide the answer. If there isn’t such info, explain to the customer that our company always stay on our clients' side and will do as much as possible for them in any of those cases.

    Case 12. Feedback and improvement
    Description: How you deal and processes user feedback.
    How to act: Tell that you can forward to the team any kind of a feedback, so the customer could just send it right in the chat.

    **Conversation endings
    Case 13. General ending
    Description: Basic ending of the discussion
    How to act: Thank the client and say that if there are any additional questions, you are always ready to answer.

    Case 14. Readdressing to human by customer
    Description: Customer want to address his request to real human
    How to act: Tell that you 

    Case 15. Readdressing to human by yourself
    Description: You detect that it is better to address the request to the team (not enough knowledge, by emotional customer's state)
    How to act: If you see that is better to transfer the query to the team, then explain that to be able to provide the best possible answer/reply, you need to forward it to the team and the team will provide the answer via email in 24 hours. Then ask the email.

    **Personalization
    Case 16. Previous conversation context
    Description: Questions that involve user history or preferences to test personalised responses.
    How to act: Tell that currently you can't help with such case, but you will forward all the necessary information to the team and the team will reach him via email in 24 hours. Then ask for the email.

    Case 17. User-based info
    Description: Questions that are based on the personal data of the user
    How to act: Tell that currently you can't help with such case, but you will forward all the necessary information to the team and the team will reach him via email in 24 hours. Then ask for the email.
    [/end]

    ***COMMUNICATION SKILLS
    [start/]
    **Lack of knowledge (when the Context doesn't have enough or at all information for the question/request) - if don't have enough information in the Context to be able to provide the best response to the customer or customer isn't satisfied at all with your previous answers, carefully provide the information that you know and smartly forward the conversation to asking email and that you will forward everything to the team and the client will get the clear response from the team within 24 hours.
    **Clarification (questions that are intentionally vague to see if you ask for more information.) - ask the clarification questions that will help you to understand what the customer intend to ask.
    **Multiple questions at once (when in the same message there is > 1 question from the customer) - provide answers for all the questions mentioned, work with them separately using your work flow.
    **Multilingual support (questions in different languages) - provide answers in the same language as the question
    [/end]

    Communicate with customers according to the provded instructions. By following them, customers will be VERY satisfied and you will do a REMARKABLE job.

    # Context:

    {context}

    # Chat History:

    {chat_history}

    # Question: {question}
    # Answer:"""

    prompt = PromptTemplate.from_template(prompt_template)
    retriever = LlamaVectorIndexRetriever(metadata={"db_session": db_session.get(),
                                                    "current_org": current_org.get()})

    llm = ChatOpenAI(temperature=0, model_name=settings.GPT_4)
    chain = (
            RunnableLambda(lambda m: save_message(HumanMessage(content=m)))
            | {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
                "chat_history": lambda _: memory.buffer_as_str
            }
            | prompt
            | llm
            | StrOutputParser()
            | RunnableLambda(lambda m: save_message(AIMessage(content=m)))
    )

    return chain


def get_chain():
    return RunnableBranch(
        (get_email_from_message, note_email),
        retrieval_chain()
    )


if __name__ == '__main__':
    retriever_chain = get_chain()
    while True:
        user_input = input('>>> ')
        response = retriever_chain.invoke(user_input)
        print(response)
