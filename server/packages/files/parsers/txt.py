from langchain.document_loaders import TextLoader
from models import File

from .common import process_file


def process_txt(
        file: File,
        brain_id,
):
    return process_file(
        file=file,
        loader_class=TextLoader,
        brain_id=brain_id,
    )
