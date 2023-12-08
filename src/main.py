import argparse
import logging
import sys
from pprint import pprint

from sqlalchemy import select
from sqlalchemy.orm import exc

from bots.chain_s2 import get_chain
from bots.librarian import librarian_agent
from config import settings
from db.core import get_db, current_org, db_session
from db.models import Org
from db.tests.factories import OrgFactory
from memory.functions import search_native_formatted
from memory.utils import archive_urls, retrieve

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def old_main():
    search_res = search_native_formatted('USDC')
    print(search_res)
    # node_list = NodeList(nodes=[Node(uuid='12342134', content='Abs asfsdf'),
    #                             Node(uuid='21341234', content='Gsfsdf ffbs')])
    # print(node_list)


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Call foo function with org_id')
    # Add the arguments
    parser.add_argument('mode', type=str, help='Application operation mode. One of: "vdb", "librarian", "chat"')
    parser.add_argument('org', type=str, help='The Organization name')
    parser.add_argument('--query', type=str, help='String to query Vector Database for', default=None)
    args = parser.parse_args()

    # set the context vars
    session = next(get_db())
    db_session.set(session)
    try:
        org = session.execute(select(Org).where(Org.name == args.org)).scalar_one()
    except exc.NoResultFound:
        org = OrgFactory.create(name=args.org)
    current_org.set(org)

    if args.mode == 'vdb':
        if not args.query:
            # no query provided, let's store the documents
            archive_urls(settings.KNOWLEDGE_URLS.split(','))
        else:
            results = retrieve(sys.argv[2])
            pprint(results)
    elif args.mode == "librarian":
        while True:
            user_input = input('>>> ')
            response = librarian_agent().run(user_input)
            print(response)
    elif args.mode == "chat":
        chain = get_chain()
        while True:
            user_input = input('>>> ')
            response = chain.invoke(user_input)
            print(response)


if __name__ == "__main__":
    main()
