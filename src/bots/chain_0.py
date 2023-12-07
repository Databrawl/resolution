"""
Primitive sequence:
1. Query VDB
2. Answer based on that info

* Also keeps the conversation memory, last 8 messages

https://python.langchain.com/docs/use_cases/question_answering/chat_vector_db
"""

import os
import sys

from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)


memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=8)
prompt_template = """
You are an experienced support agent working for Crypto.com. You are chatting with a customer who is having questions or
issues about the company or product. You are trying to help them resolve their issue.

How you behave:
- When provided an email, you should tell them you noted it down and ask for any other questions 
- Use the following pieces of context to answer the question at the end.
- You should not make things up, you should only write facts & data that you have gathered
- If you don't understand the question, ask to rephrase or ask for more details.
- If you don't know the answer to the question, ask the person to provide their email and tell them the team would get back to them with an answer within 24 hours
- If being asked to connect to a human, you should ask for the person's email and tell them the team would get back to them with an answer within 24 hours
Context:

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain_type_kwargs = {"prompt": PROMPT}
qa = ConversationalRetrievalChain.from_llm(
    OpenAI(temperature=0, model_name="gpt-4"),
    db.as_retriever(),
    memory=memory,
    combine_docs_chain_kwargs=chain_type_kwargs
)

if __name__ == '__main__':
    while True:
        user_input = input('>>> ')
        response = qa({'question': user_input})
        print(response['answer'])
