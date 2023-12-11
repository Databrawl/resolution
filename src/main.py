import argparse
import logging
from pprint import pprint

from sqlalchemy import select
from sqlalchemy.orm import exc

from bots.chain_s3 import get_chain
from bots.librarian import librarian_agent
from config import settings
from db.core import get_db, current_org, db_session
from db.models import Org
from db.tests.factories import OrgFactory
from memory.utils import archive_urls, retrieve

logging.basicConfig(level=settings.LOG_LEVEL)
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
            archive_urls(settings.KNOWLEDGE_URLS.split(','), args.crawl_depth)
        else:
            results = retrieve(args.query)
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
