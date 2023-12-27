from multiprocessing import get_logger

from supabase import create_client
from supabase.client import Client

from settings import app_settings

logger = get_logger()


def list_files_from_storage(path):
    supabase_client: Client = create_client(app_settings.SUPABASE_URL, app_settings.SUPABASE_KEY)

    try:
        response = supabase_client.storage.from_("quivr").list(path)
        logger.info("RESPONSE", response)
        return response
    except Exception as e:
        logger.error(e)
