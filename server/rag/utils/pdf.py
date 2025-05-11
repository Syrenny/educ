import fitz


def smart_fix(text: str) -> str:
    _t = ""
    for c in text:
        try:
            _t += c.encode("latin1").decode("cp1251")
        except UnicodeEncodeError:
            _t += c
    return _t


def read_pdf(file: bytes) -> str:
    """
    Extracts text from a PDF file and returns it as a single string.

    :param file: PDF file in bytes
    :return: Concatenated text from all pages
    """
    doc = fitz.open(stream=file, filetype="pdf")
    return "\n".join(smart_fix(page.get_text("text")) for page in doc)
