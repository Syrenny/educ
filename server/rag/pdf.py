import tempfile

import fitz
from bs4 import BeautifulSoup, Tag
from grobid_client.grobid_client import GrobidClient

from server.config import config

relevant_sections = {
    "abstract": "## ABSTRACT",
    "title": "#",
    "p": "",
    "head": "##",
    "body": "",
    "text": "",
    "div": "",
}


def xml2md(element: Tag, level: int = 0):
    """Recursively print XML tree using BeautifulSoup, skipping ignored tags."""
    for child in element.find_all(recursive=False):
        if isinstance(child, Tag):
            yield from xml2md(child, level + 1)
    if element.name in relevant_sections:
        for ref in element.find_all("ref"):
            if ref.has_attr("target"):
                ref_text = ref.get_text(strip=True) or ref["target"]
                link = ref["target"].lstrip("#")
                markdown_link = f"[{ref_text}](#{link})"
                ref.replace_with(markdown_link)
        text = element.get_text(strip=True)
        if text:
            yield f"{relevant_sections[element.name]} {text}"


def parse_sections_from_bytes(pdf_bytes: bytes) -> str:
    client = GrobidClient(grobid_server=config.grobid_base)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_pdf.flush()  # чтобы данные точно записались
        xml_text = client.process_pdf(
            service="processFulltextDocument",
            pdf_file=temp_pdf.name,
            generateIDs=False,
            consolidate_header=False,
            consolidate_citations=False,
            include_raw_citations=True,
            include_raw_affiliations=True,
            tei_coordinates=False,
            segment_sentences=False,
        )[2]

    # Парсинг через BeautifulSoup
    soup = BeautifulSoup(xml_text, "xml")

    # ✅ Отрисовка дерева TEI-документа (в проде закомментировать)
    print("XML дерево TEI-документа:")
    root = soup.find("TEI")
    sections = []

    if root:
        for section in xml2md(root):
            sections.append(section)

    return "\n".join(sections)


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
