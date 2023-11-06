import logging

from config import settings
from functions import search_native_formatted

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def main():
    search_res = search_native_formatted('USDC')
    print(search_res)
    # node_list = NodeList(nodes=[Node(uuid='12342134', content='Abs asfsdf'),
    #                             Node(uuid='21341234', content='Gsfsdf ffbs')])
    # print(node_list)


if __name__ == "__main__":
    main()
