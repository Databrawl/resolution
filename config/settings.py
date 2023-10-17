import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
INSTRUCTIONS = 'guardian'  # Specify the instruction prompt to use (check 'instructions' folder for valid prompts)
MAX_SEARCH_RESULTS = 4  # Set the maximum search results for internet access DONT SET TOO HIGH
MAX_TOKENS_GPT_35 = 4096
MAX_TOKENS_GPT_35_16 = 16_385
MAX_TOKENS_GPT_4 = 8192
