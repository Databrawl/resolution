import os
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.schema.retriever import BaseRetriever, Document

from src.config import settings
from src.functions import NodeList


class ChromaIDRetriever(BaseRetriever):
    db_path: str

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        """
        _get_relevant_documents is function of BaseRetriever implemented here

        :param query: String value of the query

        """
        client = chromadb.PersistentClient(path=self.db_path)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.environ["OPENAI_API_KEY"],
            model_name="text-embedding-ada-002"
        )
        collection = client.get_collection(name="langchain", embedding_function=openai_ef)
        search_results = collection.query(query_texts=[query], n_results=5)

        results = []
        for _id, doc in zip(search_results['ids'][0], search_results['documents'][0]):
            results.append(Document(uuid=_id, content=doc))

        return NodeList(nodes=results)


retriever_r = ChromaIDRetriever(db_path=settings.CHROMA_DIRECTORY)

llm = ChatOpenAI(temperature=0, model_name='gpt-4')
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type='map_reduce',
    retriever=retriever_r,
    chain_type_kwargs={"question_prompt": 'PROMPT', "combine_prompt": 'Combine Prompt'},
    verbose=True
)
