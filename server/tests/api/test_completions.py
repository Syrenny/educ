import json
import time

import pytest


@pytest.mark.asyncio
async def test_chat_completions(client, headers, valid_pdf, upload_files_headers):
    # Шаг 1: Загружаем файл
    files = [("files", ("test.pdf", valid_pdf, "application/pdf"))]
    response = await client.post("/files", files=files, headers=upload_files_headers)

    filename = response.json()[0]["filename"]
    file_id = response.json()[0]["file_id"]

    assert response.status_code == 200
    assert filename == "test.pdf"

    # Шаг 2: Ожидаем завершения индексации
    indexing_done = False
    max_retries = 30
    retries = 0
    while not indexing_done and retries < max_retries:
        status_response = await client.get(f"/files/{file_id}/status", headers=headers)
        if status_response.status_code == 200:
            indexing_done = status_response.json()

        if not indexing_done:
            retries += 1
            time.sleep(1)

    print("Num retries:", retries)
    assert indexing_done, "File indexing did not complete in time"

    # Шаг 3: Запрашиваем stream_id для чата
    request_data = {
        "messages": [
            {
                "role": "user",
                "content": "Декоратор field_validator всегда принимает один обязательный аргумент - название поля, которое необходимо валидировать. Второй аргумент, который предпочтительно указывать, mode.",
            }
        ],
        "documents": [{"filename": filename, "file_id": file_id}],
        "snippet": "",
        "action": "default",
    }

    # Подготавливаем поток
    prepare_response = await client.post(
        "/api/prepare_stream", json=request_data, headers=headers
    )
    stream_id = prepare_response.json()

    assert prepare_response.status_code == 200

    # Шаг 4: Получаем поток данных
    completion_params = {
        "method": "GET",
        "url": f"/api/v1/chat/completions?stream_id={stream_id}",
        "headers": headers,
    }

    response_text = ""
    found_done = False
    async with client.stream(**completion_params) as response:
        assert response.status_code == 200
        async for chunk in response.aiter_lines():
            if chunk and chunk.startswith("data: "):
                json_part = chunk[len("data: ") :]
                if json_part == "[DONE]":
                    found_done = True
                else:
                    parsed = json.loads(json_part)
                    assert "choices" in parsed
                    assert len(parsed["choices"]) > 0
                    assert "delta" in parsed["choices"][0]
                    assert "content" in parsed["choices"][0]["delta"]
                    response_text += parsed["choices"][0]["delta"]["content"]

    assert found_done, "Streaming response did not include [DONE] marker"
    assert response_text.strip(), "Response text is empty"
