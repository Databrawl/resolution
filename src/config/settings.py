import logging
import os
import sys

from dotenv import find_dotenv, load_dotenv

ENV = os.getenv('ENV', 'local')
if ENV == 'prod':
    logging.info('⚠️ Running in a production mode ⚠️')

DOTENV_FILE = f'{ENV}.env'
load_dotenv(find_dotenv(DOTENV_FILE))

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

sys.path.append(SRC_ROOT)


def load_instructions(name):
    with open(os.path.join(PROJECT_ROOT, 'instructions', f'{name}.txt'), 'r') as f:
        return f.read()


LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
KNOWLEDGE_URLS = os.getenv('KNOWLEDGE_URLS')
RESULT_SEPARATOR = ' -:- '
GPT_35 = 'gpt-3.5-turbo-1106'
GPT_4 = 'gpt-4-1106-preview'
INTERNET_ACCESS = True  # Set to true to enable internet access
# To add custom prompts, create a .txt file like 'custom.txt' in `instructions` folder and set INSTRUCTIONS as 'custom'
SUPPORT_AGENT_INSTRUCTIONS = load_instructions('support_agent-3')
REVIEWER_INSTRUCTIONS = load_instructions('reviewer')
MAX_SEARCH_RESULTS = 4  # Set the maximum search results for internet access DONT SET TOO HIGH
MAX_TOKENS_GPT_35 = 4096
MAX_TOKENS_GPT_35_16 = 16_385
MAX_TOKENS_GPT_4 = 8192
AUTOGEN_CONFIG_LIST = [
    {
        'model': GPT_4,
        'api_key': OPENAI_API_KEY,
    },  # OpenAI API endpoint for gpt-3.5-turbo-16k
]

# Supabase configs
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
SUPABASE_DB_USER: str = os.environ.get("SUPABASE_DB_USER")
SUPABASE_DB_PASSWORD: str = os.environ.get("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST: str = os.environ.get("SUPABASE_DB_HOST")
SUPABASE_DB_PORT: int = int(os.environ.get("SUPABASE_DB_PORT"))
SUPABASE_DB_NAME: str = os.environ.get("SUPABASE_DB_NAME")
SUPABASE_DB = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/" \
              f"{SUPABASE_DB_NAME}"
SUPABASE_DOCUMENTS_TABLE = "documents"

# Llamaindex configs
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
