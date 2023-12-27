import argparse
import logging
from pprint import pprint

from langchain.globals import set_verbose
from sqlalchemy import select
from sqlalchemy.orm import exc

from bots.agent_5 import get_agent
from bots.librarian import librarian_agent
from db import db
from db.models import Org
from db.tests.factories import OrgFactory
from memory.utils import archive_urls, retrieve
from settings import app_settings

logging.basicConfig(level=app_settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# TODO:
# 1. Fix URL parsing list error
# 2. Fix Wandb session serializing
def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Call foo function with org_id')
    # Add the arguments
    parser.add_argument('mode', type=str,
                        help='Application operation mode. One of: "vdb", "librarian", "chat"')
    parser.add_argument('org', type=str, help='The Organization name')
    parser.add_argument('--query', type=str, help='String to query Vector Database for',
                        default=None)
    parser.add_argument('--crawl_depth', type=int,
                        help='Depth of crawl of the URLs, default is 0 - no crawl',
                        default=0)
    args = parser.parse_args()

    with db.session:
        try:
            org = db.session.execute(select(Org).where(Org.name == args.org)).scalar_one()
        except exc.NoResultFound:
            org = OrgFactory.create(name=args.org)
        Org.current.set(org)

        if args.mode == 'vdb':
            if not args.query:
                # no query provided, let's store the documents
                archive_urls(app_settings.KNOWLEDGE_URLS.split(','), args.crawl_depth)
            else:
                results = retrieve(args.query)
                pprint(results)
        elif args.mode == "librarian":
            while True:
                user_input = input('>>> ')
                response = librarian_agent().run(user_input)
                print(response)
        elif args.mode == "chat":
            agent = get_agent()

            set_verbose(True)
            # set_debug(True)
            while True:
                user_input = input('>>> ')
                response = agent.run(user_input)

                print(response)


if __name__ == "__main__":
    main()
