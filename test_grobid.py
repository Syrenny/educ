import asyncio
import json
from pathlib import Path

from server.rag import parse_sections_from_bytes

if __name__ == "__main__":
    # Укажи путь к PDF-файлу
    file_path = Path("server/tests/files/valid.pdf")
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    with file_path.open("rb") as f:
        pdf_bytes = f.read()

    try:
        sections = asyncio.run(parse_sections_from_bytes(pdf_bytes))
        # Используем model_dump() вместо model_dump_json()
        with open("valid-sections.json", "w", encoding="utf-8") as f:
            json.dump(
                [section.model_dump() for section in sections],
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception as e:
        import traceback

        print(f"Ошибка при разборе статьи: {e}")
        traceback.print_exc()
