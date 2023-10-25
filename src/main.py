import logging

from src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)



def main():
    return True


if __name__ == "__main__":
    main()
