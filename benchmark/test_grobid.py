import time
from pathlib import Path

from server.rag import parse_sections_from_bytes
from server.utils.llm import get_langchain_embeddings


def split_into_sentences(text: str) -> list[str]:
    import re

    # Простое разбиение на предложения (можно заменить на nltk или spacy)
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s]


if __name__ == "__main__":
    embedder = get_langchain_embeddings()

    file_path = Path("/home/syrenny/Documents/cormen.pdf")
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    with file_path.open("rb") as f:
        pdf_bytes = f.read()

    # PDF -> markdown

    start_time = time.time()

    md = parse_sections_from_bytes(pdf_bytes)
    print("GROBID Done")

    sentences = split_into_sentences(md)

    print(f"Предложений для векторизации: {len(sentences)}")

    embeddings = embedder.embed_documents(sentences)

    print(f"Общее время: {time.time() - start_time:.2f} сек.")
