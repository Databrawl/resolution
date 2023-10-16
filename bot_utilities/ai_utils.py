import json
import logging

import openai
import requests
from bs4 import BeautifulSoup
from langchain import PromptTemplate
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def sdxl(prompt):
    response = openai.Image.create(
        model="sdxl",
        prompt=prompt,
        n=1,  # images count
        size="1024x1024"
    )
    return response['data'][0]["url"]


def knowledge_retrieval(query):
    # Define the data to be sent in the request
    logger.info('We are in the knowledge retrieval function')
    data = {
        "params": {
            "query": query
        },
        "project": "feda14180b9d-4ba2-9b3c-6c721dfe8f63"
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    response = requests.post(
        "https://api-1e3042.stack.tryrelevance.com/latest/studios/6eba417b-f592-49fc-968d-6b63702995e3/trigger_limited",
        data=data_json)

    # Check the response status code
    if response.status_code == 200:
        return response.json()["output"]["answer"]
    else:
        print(f"HTTP request failed with status code {response.status_code}")


def summary(content):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])
    map_prompt = """
    Write a summary of the following text:
    "{text}"
    SUMMARY:
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )

    output = summary_chain.run(input_documents=docs, )

    return output


def scrape_website(url: str):
    # scrape website, and also will summarize the content based on objective if the content is too large
    # objective is the original objective & task that user give to the agent, url is the url of the website to be scraped

    print("Scraping website...")
    # Define the headers for the request
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # Define the data to be sent in the request
    data = {
        "url": url
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    response = requests.post("https://chrome.browserless.io/content?token=0a049e5b-3387-4c51-ab6c-57647d519571",
                             headers=headers, data=data_json)

    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print("CONTENTTTTTT:", text)
        if len(text) > 10000:
            output = summary(text)
            return output
        else:
            return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")


def search(query):
    """
    Asynchronously searches for a prompt and returns the search results as a blob.

    Args:
        prompt (str): The prompt to search for.

    Returns:
        str: The search results as a blob.

    Raises:
        None
    """

    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query
    })
    headers = {
        'X-API-KEY': 'ab179d0f00ae0bafe47f77e09e62b9f53b3f281d',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def research_agent(id, user_name, ai_name, instructions):
    system_message = SystemMessage(
        content=instructions
    )

    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
        "system_message": system_message,
    }

    memory = ConversationBufferWindowMemory(memory_key="memory", return_messages=True, ai_prefix=ai_name,
                                            user_prefix=user_name)

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    tools = [
        Tool(
            name="Knowledge_retrieval",
            func=knowledge_retrieval,
            description="Use this to get our internal knowledge base data for curated information, always use this first before searching online"
        ),
        Tool(
            name="Google_search",
            func=search,
            description="Always use this to answer questions about current events, data, or terms that you don't really understand. You should ask targeted questions"
        ),
        Tool(
            name="Scrape_website",
            func=scrape_website,
            description="Use this to load content from a website url"
        ),
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=False,
        agent_kwargs=agent_kwargs,
        memory=memory
    )

    agents[id] = agent

    return agent


agents = {}


def create_agent_wrapper(id, user_name, ai_name, instructions):
    system_message = SystemMessage(
        content=instructions
    )

    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
        "system_message": system_message,
    }

    memory = ConversationBufferWindowMemory(memory_key="memory", return_messages=True, ai_prefix=ai_name,
                                            user_prefix=user_name)

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    tools = [
        Tool(
            name="research",
            func=research_agent,
            description="Always use this to answer questions about current events, data, or terms that you don't really understand. You should ask targeted questions"
        ),
        Tool(
            name="Scrape_website",
            func=scrape_website,
            description="Use this to load content from a website url"
        ),
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory
    )

    agents[id] = agent

    return agent


def generate_response(instructions, user_input):
    id = user_input["id"]
    message = user_input["message"]

    if id not in agents:
        user_name = user_input["user_name"]
        ai_name = user_input["ai_name"]
        # agent = create_agent_wrapper(id, user_name, ai_name, instructions)
        agent = research_agent(id, user_name, ai_name, instructions)
    else:
        agent = agents[id]

    print(message)
    response = agent.run(message)

    return response
