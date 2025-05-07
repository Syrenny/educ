import json
import time

import pytest


@pytest.mark.asyncio
async def test_history_with_shortcut(
    client,
    headers,
    valid_pdf,
    upload_files_headers,
):
    # Шаг 1: загрузка файла
    files = [("files", ("test.pdf", valid_pdf, "application/pdf"))]
    upload_response = await client.post(
        "/files", files=files, headers=upload_files_headers
    )
    assert upload_response.status_code == 200
    file_info = upload_response.json()[0]
    file_id = file_info["file_id"]
    filename = file_info["filename"]

    # Шаг 2: дожидаемся индексации
    for _ in range(30):
        status_response = await client.get(f"/files/{file_id}/status", headers=headers)
        if status_response.status_code == 200 and status_response.json() is True:
            break
        time.sleep(1)
    else:
        assert AssertionError(), "Индексация файла не завершилась вовремя"

    # Шаг 3: Отправляем запрос в /v1/chat/completions с shortcut
    request_data = {
        "messages": [{"role": "user", "content": ""}],
        "documents": [{"filename": filename, "file_id": file_id}],
        "snippet": "Text snippet",
        "action": "explain",
    }

    completion_params = {
        "method": "POST",
        "url": "/v1/chat/completions",
        "json": request_data,
        "headers": headers,
    }

    async with client.stream(**completion_params) as response:
        assert response.status_code == 200
        async for chunk in response.aiter_lines():
            if chunk.startswith("data: "):
                data = chunk.removeprefix("data: ")
                if data == "[DONE]":
                    break
                parsed = json.loads(data)
                assert "choices" in parsed

    # Шаг 4: получаем историю
    response = await client.get(f"/history/{file_id}", headers=headers)
    assert response.status_code == 200

    history = response.json()
    assert len(history) == 2

    msg = history[0]
    assert msg["content"] == ""
    assert msg["is_user"] is True
    assert "timestamp" in msg

    assert msg["action"] == "explain"
    assert msg["snippet"] == "Text snippet"
