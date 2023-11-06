import logging
import os
import sys
from pprint import pprint

import bs4
import requests

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)

# nest_asyncio.apply()

# initialize simple vector indices


years = [2022, 2021, 2020, 2019]

# loader = UnstructuredReader()
# UnstructuredURLLoader = download_loader("UnstructuredURLLoader")


### Step 1: Load remote data into memory and prepare for indexing
urls = [
    "https://crypto.com/eea/cards",
    # "https://crypto.com/eea/earn",
    # "https://crypto.com/eea/about",
    # "https://crypto.com/eea/careers",
    # "https://crypto.com/eea",
    # "https://crypto.com/eea/fftb",
    # "https://crypto.com/eea/security",
    # "https://crypto.com/eea/partners",
    # "https://crypto.com/eea/defi-wallet"
]

# web_loader = WebBaseLoader(urls)
# documents = web_loader.load()
# for doc in documents:
#     loader.load_data(doc, split_documents=False)
COMPRESS_PROMPT = """# MISSION
You are a Sparse Priming Representation (SPR) writer. An SPR is a particular kind of use of language for advanced NLP, NLU, and NLG tasks, particularly useful for the latest generation Large Language Models (LLMs). You will be given information by the USER which you are to render as an SPR.

# THEORY
LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as latent space. The latent space of a LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are associative, meaning you only need to use the correct associations to "prime" another model to think in the same way.

# METHODOLOGY
Render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human."""

# loader = UnstructuredURLLoader(urls=urls, continue_on_failure=False, headers={"User-Agent": "value"})
# loader.load()

logger = logging.getLogger(__name__)

html = requests.get(urls[0], headers={"User-Agent": "value"}).text
text = bs4.BeautifulSoup(html, "html.parser").text
print('BS version')
print(text)

from unstructured.partition.html import partition_html

## Data pre-processing pipeline
for url in urls:
    # 1. Partition
    elements = partition_html(url=url, skip_headers_and_footers=True, infer_table_structure=True)

    # # 2. Clean
    from unstructured.cleaners.core import clean_bullets, clean_dashes, clean_extra_whitespace, \
        clean_non_ascii_chars, clean_ordered_bullets, clean_trailing_punctuation, group_broken_paragraphs, \
        replace_unicode_quotes

    clean_elements = []
    for element in elements:
        old_text = element.text
        try:
            element.apply(
                clean_bullets,
                clean_dashes,
                clean_extra_whitespace,
                clean_non_ascii_chars,
                clean_ordered_bullets,
                clean_trailing_punctuation,
                group_broken_paragraphs,
                replace_unicode_quotes
            )
        except Exception as e:
            logger.warning('got exception while cleaning element: ' + str(e))
        else:
            clean_elements.append(element)

            # if element.text != old_text:
            #     print("#### text before: ")
            #     print(old_text)
            #     print("#### text after: ")
            #     print(element.text)

    # 3. Chunk
    from unstructured.chunking.title import chunk_by_title

    chunks = chunk_by_title(elements)

    for i, chunk in enumerate(chunks):
        print('')
        pprint(chunk.text)
        print("\n\n" + "-" * 80)

# elements = partition(str(file))
# 4. Create an embedding for each chunk (either via
#   a. Unstructured https://unstructured-io.github.io/unstructured/bricks/embedding.html
#   OR
#   a. Llama Index


######################################################
# doc_set = {}
# all_docs = []
# for year in years:
#     year_docs = loader.load_data(
#         file=Path(f"./data/UBER/UBER_{year}.html"), split_documents=False
#     )
#     # insert year metadata into each year
#     for d in year_docs:
#         d.metadata = {"year": year}
#     doc_set[year] = year_docs
#     all_docs.extend(year_docs)
#
# index_set = {}
# service_context = ServiceContext.from_defaults(chunk_size=512)
# for year in years:
#     storage_context = StorageContext.from_defaults()
#     cur_index = VectorStoreIndex.from_documents(
#         doc_set[year],
#         service_context=service_context,
#         storage_context=storage_context,
#     )
#     index_set[year] = cur_index
#     storage_context.persist(persist_dir=f"./storage/{year}")
#
# years = [2022, 2021, 2020, 2019]
#
# loader = UnstructuredReader()
# doc_set = {}
# all_docs = []
# for year in years:
#     year_docs = loader.load_data(
#         file=Path(f"./data/UBER/UBER_{year}.html"), split_documents=False
#     )
#     # insert year metadata into each year
#     for d in year_docs:
#         d.metadata = {"year": year}
#     doc_set[year] = year_docs
#     all_docs.extend(year_docs)
#
# # Load indices from disk
#
# index_set = {}
# for year in years:
#     storage_context = StorageContext.from_defaults(persist_dir=f"./storage/{year}")
#     cur_index = load_index_from_storage(
#         storage_context, service_context=service_context
#     )
#     index_set[year] = cur_index
#
# individual_query_engine_tools = [
#     QueryEngineTool(
#         query_engine=index_set[year].as_query_engine(),
#         metadata=ToolMetadata(
#             name=f"vector_index_{year}",
#             description=f"useful for when you want to answer queries about the {year} SEC 10-K for Uber",
#         ),
#     )
#     for year in years
# ]
#
# query_engine = SubQuestionQueryEngine.from_defaults(
#     query_engine_tools=individual_query_engine_tools,
#     service_context=service_context,
# )
#
# query_engine_tool = QueryEngineTool(
#     query_engine=query_engine,
#     metadata=ToolMetadata(
#         name="sub_question_query_engine",
#         description="useful for when you want to answer queries that require analyzing multiple SEC 10-K documents for Uber",
#     ),
# )
#
# tools = individual_query_engine_tools + [query_engine_tool]
#
# agent = OpenAIAgent.from_tools(tools, verbose=True)
#
# response = agent.chat("hi, i am bob")
# print(str(response))
#
# response = agent.chat("What were some of the biggest risk factors in 2020 for Uber?")
# print(str(response))
#
# agent = OpenAIAgent.from_tools(tools)  # verbose=False by default
#
# while True:
#     text_input = input("User: ")
#     if text_input == "exit":
#         break
#     response = agent.chat(text_input)
#     print(f"Agent: {response}")
