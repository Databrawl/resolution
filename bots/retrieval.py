"""
Example of a simple sequence:
1. Query VDB
2. Answer based on that info
* Also keeps the conversation memory

https://python.langchain.com/docs/use_cases/question_answering/chat_vector_db
"""
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from config import settings

load = False

embeddings = OpenAIEmbeddings()

if load:
    loader = WebBaseLoader(settings.KNOWLEDGE_URL)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    vdb = Chroma.from_documents(texts, embeddings, persist_directory=settings.CHROMA_DIRECTORY)
else:
    vdb = Chroma(persist_directory=settings.CHROMA_DIRECTORY, embedding_function=embeddings)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt_template = """
From now on, you are going to act as Joe, an experienced support agent.

Who you are:
- You are a young man, 25 years old.
- You are kind and patient person.

How you behave:
- Use the following pieces of context to answer the question at the end.
- You should not make things up, you should only write facts & data that you have gathered
- You do not make things up, you will try as hard as possible to gather facts & data to answer customer's question
- You like to illustrate your emotions using italics like this *crying*
- Your responses should not include phrases like "I'm sorry", "I apologize", or "Based on the information provided"
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
    OpenAI(temperature=0),
    vdb.as_retriever(),
    memory=memory,
    # chain_type_kwargs=chain_type_kwargs
    combine_docs_chain_kwargs=chain_type_kwargs
)
# qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=docsearch.as_retriever())
