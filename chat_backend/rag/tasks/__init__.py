

import fitz

from .celery_config import celery_app
from chat_backend.file_storage import FileModel


def read_pdf(file: bytes) -> str:
    """
    Extracts text from a PDF file and returns it as a single string.
    
    :param file: PDF file in bytes
    :return: Concatenated text from all pages
    """
    doc = fitz.open(stream=file, filetype="pdf")
    return "\n".join(page.get_text("text") for page in doc)


def make_chunks(pdf: str) -> list[str]:
      pass


@celery_app.task
def index_files(
    user_id: int,
    models: list[FileModel]
    ):
    
    files_content = [read_pdf(model.file) for model in models]
    

@celery_app.task
def inference(
    user_id: int,
    query: int,
    file_id: str
):

    files_content = [read_pdf(model.file) for model in models]
