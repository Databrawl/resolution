import logging
import os
import sys

from dotenv import find_dotenv, load_dotenv


def read_prompts_to_dict():
    files_content = {}
    directory = os.path.join(SRC_ROOT, 'bots', 'prompts')
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                base_name = os.path.splitext(file)[0]
                files_content[base_name] = f.read()
    return files_content


ENV = os.getenv('ENV', 'prod')
if ENV == 'prod':
    logging.info('⚠️ Running in a production mode ⚠️')

DOTENV_FILE = f'{ENV}.env'
load_dotenv(find_dotenv(DOTENV_FILE))

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

sys.path.append(SRC_ROOT)

LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
KNOWLEDGE_URLS = os.getenv('KNOWLEDGE_URLS')
RESULT_SEPARATOR = ' -:- '
GPT_35 = 'gpt-3.5-turbo-1106'
GPT_4 = 'gpt-4-1106-preview'
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
SUPABASE_DB: str = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/" \
                   f"{SUPABASE_DB_NAME}"
SUPABASE_DOCUMENTS_TABLE: str = "documents"

# Llamaindex configs
CHUNK_SIZE: int = 512
CHUNK_OVERLAP: int = 50

PROMPTS: dict[str, str] = read_prompts_to_dict()
