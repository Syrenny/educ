import fitz
import httpx
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

from server.config import config

relevant_sections = [
    "abstract",
    "title",
    "p",
    "head",
    "body",
    "text",
]


class Section(BaseModel):
    title: str
    content: str


def extract_text_with_indent(tag: Tag, level: int = 0) -> str:
    """Recursively extract text with indentation from a BeautifulSoup tag."""
    if tag.name not in relevant_sections:
        return ""

    indent = "  " * level
    lines = []

    if tag.name in ("head", "title"):
        text = tag.get_text(strip=True)
        if text:
            lines.append(f"{indent}{text}")
    elif tag.name == "p":
        text = tag.get_text(strip=True)
        if text:
            lines.append(f"{indent}{text}")

    for child in tag.find_all(recursive=False):
        if isinstance(child, Tag):
            lines.append(extract_text_with_indent(child, level + 1))

    return "\n".join(filter(None, lines))


def print_xml_tree_bs4(element: Tag, level: int = 0):
    """Recursively print XML tree using BeautifulSoup, skipping ignored tags."""
    if element.name in relevant_sections:
        indent = "  " * level
        attrs = " ".join(f'{k}="{v}"' for k, v in element.attrs.items())
        text = (element.string or "").strip() if element.string else ""

        print(
            f"{indent}<{element.name} {attrs}> {text}"
            if attrs
            else f"{indent}<{element.name}> {text}"
        )

    for child in element.find_all(recursive=False):
        if isinstance(child, Tag):
            print_xml_tree_bs4(child, level + 1)


async def parse_sections_from_bytes(pdf_bytes: bytes) -> list[Section]:
    async with httpx.AsyncClient() as client:
        files = {
            "input": ("article.pdf", pdf_bytes, "application/pdf"),
        }

        data = {
            "includeRawCitations": "1",
        }

        response = await client.post(
            f"{config.grobid_base}/api/processFulltextDocument",
            files=files,
            data=data,
        )
        response.raise_for_status()

    # TEI-XML как текст
    xml_text = response.text

    # Парсинг через BeautifulSoup
    soup = BeautifulSoup(xml_text, "xml")

    sections = []

    # ✅ Отрисовка дерева TEI-документа (в проде закомментировать)
    print("XML дерево TEI-документа:")
    root = soup.find("TEI")
    if root:
        print_xml_tree_bs4(root)

    body = soup.find("body")
    if not body:
        return []

    for div in body.find_all("div", recursive=False):
        # Название секции
        head = div.find("head")
        title = head.get_text(strip=True) if head else "Без названия"
        # Параграфы
        paragraphs = div.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs)
        sections.append(Section(title=title, content=content))

    return sections


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
