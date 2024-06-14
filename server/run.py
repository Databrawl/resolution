import argparse
import logging
from functools import wraps
from pprint import pprint
from uuid import uuid4

from langchain.globals import set_verbose
from sqlalchemy import select
from sqlalchemy.orm import exc

import memory
from bots.librarian import librarian_agent
from bots.team import call_manager
from db import db
from db.models import Org, Chat, User
from app import app
from vdb.utils import archive_urls, retrieve, archive_files
from settings import app_settings

logging.basicConfig(level=app_settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def with_app_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)
    return decorated_function


@with_app_context
def main(mode: str, org: Org, query: str, store_files: str, crawl_depth: int, ignored_url: str) -> None:
    try:
        org = db.session.execute(select(Org).where(Org.name == org)).scalar_one()
    except exc.NoResultFound:
        org = Org(name=org)
        db.session.add(org)
    Org.current.set(org)

    if mode == 'vdb':
        if query:
            results = retrieve(query)
            pprint(results)
        elif store_files:
            archive_files(app_settings.KNOWLEDGE_DIR)
            db.session.commit()
        else:
            # no query provided, let's store the documents
            archive_urls(app_settings.KNOWLEDGE_URLS.split(','), crawl_depth, ignored_url)
            db.session.commit()
    elif mode == "librarian":
        while True:
            user_input = input('>>> ')
            if user_input == "exit":
                break
            response = librarian_agent().run(user_input)
            print(response)
            db.session.commit()
    elif mode == "chat":
        chat_name = str(uuid4())
        user = db.session.query(User).first()
        chat = Chat(name=chat_name, user=user)
        db.session.add(chat)
        chat_memory = memory.load(chat.id)

        agent = call_manager(chat_memory)

        set_verbose(True)
        while True:
            user_input = input('>>> ')
            response = agent.run(user_input)
            memory.save(chat.id, user_input, response)

            print(response)


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Call foo function with org_id')
    # Add the arguments
    parser.add_argument('mode', type=str,
                        help='Application operation mode. One of: "vdb", "librarian", "chat"')
    parser.add_argument('org', type=str, help='The Organization name')
    parser.add_argument('--query', type=str, help='Vector Database query string', default=None)
    parser.add_argument('--store_files', action='store_true', help='Whether to upload files to the database')
    parser.add_argument('--crawl_depth', type=int,
                        help='Depth of crawl of the URLs, default is 0 - no crawling, just scrape the given URLs',
                        default=0)
    parser.add_argument('--ignored_url', type=str, help='URL pattern to ignore', default=None)
    args = parser.parse_args()

    main(args.mode, args.org, args.query, args.store_files, args.crawl_depth, args.ignored_url)
