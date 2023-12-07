"""
Given a query, find the most relevant set of documents from VDB and update the information contained there with a new
info.

https://python.langchain.com/docs/modules/chains/how_to/openai_functions
"""
import logging
import os
import sys

from langchain.chains.openai_functions import create_structured_output_runnable
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

from memory.functions import update_documents, search_native_formatted, Node
from src.config import settings

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=8)
tickets = {}

logging.basicConfig(level=logging.DEBUG)
# TODO: 2 approaches:
#   1. Retrieve the docs in a chain, take the query as an input
#   2. Use an Agent, let him write the retrieval query first, then update the docs


# update_prompt_template = """
#     You are a Senior Data Analyst experienced in operating with Vector Data Bases. You are given an information update
#     task. What it means is that you need to find the documents that need to be updated with the new information and
#     update them.
#
#     1. Go through all the documents available in the Context
#     2. Pick those which contain the relevant information
#     3. Rewrite their content incorporating new information
#     4. Output the update function call with necessary parameters
#
#     # Context:
#
#     {context}
#
#     # New information: {text}
#
#     # Answer (make sure to answer in the correct format):
# """

update_prompt_template = """
    You are a Senior Data Analyst experienced in operating with Vector Data Bases. You are given an information update
    task. What it means is that you need to find the documents that need to be updated with the new information and
    update them. You are a world class algorithm for extracting information in structured formats.

    1. Go through all the documents available in the Context
    2. Pick those which contain the relevant information
    3. Rewrite their content incorporating new information
    4. Call the update function with necessary parameters

    # Context:

    {context}

    # New information: {text}

    # Answer (make sure to answer in the correct format):
"""
update_prompt = PromptTemplate.from_template(update_prompt_template)
llm = ChatOpenAI(temperature=0, model_name=settings.GPT_4)
# update_documents_runnable = create_openai_fn_runnable([update_documents], llm, update_prompt)
# node_list_runnable = create_structured_output_runnable(NodeList, llm, update_prompt)
node_list_runnable = create_structured_output_runnable(Node, llm, update_prompt)
# parser = PydanticOutputParser(pydantic_object=NodeList)
# full_chain = (
#         {
#             "context": lambda text: search_native_formatted(text),
#             "text": lambda text: text,
#         }
#         | update_documents_runnable
#         | update_documents_primitive_types
# )

full_chain = (
        {
            "context": lambda text: search_native_formatted(text),
            "text": lambda text: text,
        }
        | node_list_runnable
        | update_documents
)

# res = full_chain.invoke("Add new card to our product line. Update all the necessary documents: Void Black: CRO Lockup: €500,000 EUR, CRO Rewards: 6%, No annual fees, Top-up with cash only, Enjoy up to 6% back on all spending with your sleek titanium card, Access to Crypto Earn to earn interest on your assets, Access to Crypto.com Exchange for trading cryptocurrencies")
# res = full_chain.invoke("Change the CRO lockup period to 20 days.")
res = full_chain.invoke("We brought back support of USDC.")

print(res)
