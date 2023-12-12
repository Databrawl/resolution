"""
https://blog.gopenai.com/clustering-financial-news-using-bertopic-and-gpt-in-5-simple-steps-4e2f7a80c959

https://dylancastillo.co/clustering-documents-with-openai-langchain-hdbscan/
"""

import hdbscan
import pandas as pd
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from config import settings


def get_prompt():
    system_template = "You're an expert customer support manager. You're helping to categorize a " \
                      "set of support tickets based on their intent."
    human_template = "Using the following customer support tickets, write a category description " \
                     "that they have in common.\n\nTICKETS:{tickets}\n\nCATEGORY:"

    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template),
        ],
        input_variables=["tickets"],
    )


def _summarize_clusters(df):
    results = []
    for c in df.cluster.unique():
        chain = LLMChain(
            llm=ChatOpenAI(temperature=0, model_name=settings.GPT_4), prompt=get_prompt(),
            verbose=False
        )
        tickets_str = "\n\n\n\n".join(
            [f"{row['item']}" for row in df.query(f"cluster == {c}").to_dict(orient="records")])
        result = chain.run(
            {
                "tickets": tickets_str,
            }
        )
        results.append(result)

    return results


def cluster(items: list[str]) -> list[str]:
    """
    Cluster a list of items using HDBSCAN with OpenAI embeddings + OpenAI GPT-4 summarization
    """
    embeddings = OpenAIEmbeddings(chunk_size=1000).embed_documents(items)
    hdb = hdbscan.HDBSCAN(min_samples=3, min_cluster_size=3).fit(embeddings)

    df = pd.DataFrame({
        "item": items,
        "cluster": hdb.labels_,
    })
    df = df.query("cluster != -1")  # Remove documents that are not in a cluster

    return _summarize_clusters(df)
