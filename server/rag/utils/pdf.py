import fitz


def read_pdf(file: bytes) -> str:
    """
    Extracts text from a PDF file and returns it as a single string.

    :param file: PDF file in bytes
    :return: Concatenated text from all pages
    """
    doc = fitz.open(stream=file, filetype="pdf")
    return "\n".join(page.get_text("text") for page in doc)
