import os
import sys

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

sys.path.append(SRC_ROOT)


def load_instructions(name):
    with open(os.path.join(PROJECT_ROOT, 'instructions', f'{name}.txt'), 'r') as f:
        return f.read()


LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VDB_URL = os.getenv('VDB_URL')
CHROMA_DIRECTORY = os.path.join(PROJECT_ROOT, 'chroma_db')
KNOWLEDGE_URL = os.getenv('KNOWLEDGE_URL')
RELEVANCE_PROJECT_ID = os.getenv('RELEVANCE_PROJECT_ID')
RESULT_SEPARATOR = ' -:- '
GPT_35 = 'gpt-3.5-turbo-16k-0613'
GPT_35_16 = 'gpt-3.5-turbo-16k'
GPT_4 = 'gpt-4'
INTERNET_ACCESS = True  # Set to true to enable internet access
# To add custom prompts, create a .txt file like 'custom.txt' in `instructions` folder and set INSTRUCTIONS as 'custom'
SUPPORT_AGENT_INSTRUCTIONS = load_instructions('support_agent-2')
REVIEWER_INSTRUCTIONS = load_instructions('reviewer')
MAX_SEARCH_RESULTS = 4  # Set the maximum search results for internet access DONT SET TOO HIGH
MAX_TOKENS_GPT_35 = 4096
MAX_TOKENS_GPT_35_16 = 16_385
MAX_TOKENS_GPT_4 = 8192
# FUNCTIONS_CONFIG = {
#     "functions": [
#         ,
#         {
#             "name": "scrape",
#             "description": "Scraping website content based on url",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "url": {
#                         "type": "string",
#                         "description": "Website url to scrape",
#                     }
#                 },
#                 "required": ["url"],
#             },
#         },
#     ]
# }
AUTOGEN_CONFIG_LIST = [
    {
        'model': GPT_4,
        'api_key': OPENAI_API_KEY,
    },  # OpenAI API endpoint for gpt-3.5-turbo-16k
]
