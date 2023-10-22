import logging

from bots.ai_utils import generate_response, knowledge_retrieval
from bots.autogen_support import ask
from bots.functions import search_knowledge_base

from src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)



def main():
    messages = []
    # while True:
    #     user_input = input('>>> ')
    #     # res = search_knowledge_base(user_input)
    #     res = knowledge_retrieval(user_input)
    #     print(res)
        # messages = ask(user_input, messages)
        # print('This is the final answer:')
        # print(messages[-1])




if __name__ == "__main__":
    main()
