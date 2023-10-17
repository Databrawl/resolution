import logging


from bots.ai_utils import generate_response
from bots import retrieval

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def main():
    # Open the file in read mode
    with open('instructions/guardian-2.txt', 'r') as file:
        # Read the content of the file into the variable
        instructions = file.read()

    while True:
        user_input = input('>>> ')
        response = generate_response(instructions,
                                     {'id': 0, 'message': user_input, 'user_name': 'Tyrael', 'ai_name': 'Guardian'})
        print(response)

    # while True:
    #     user_input = input('>>> ')
    #     response = retrieval.qa({'question': user_input})
    #     print(response['answer'])


if __name__ == "__main__":
    main()
