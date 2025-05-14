import time

import pytest


@pytest.mark.asyncio
async def test_history_with_shortcut(
    client,
    valid_pdf,
):
    # Шаг 1: загрузка файла
    files = [("files", ("test.pdf", valid_pdf, "application/pdf"))]
    upload_response = await client.post("/api/files", files=files)
    assert upload_response.status_code == 200
    file_info = upload_response.json()[0]
    file_id = file_info["file_id"]

    # Шаг 2: дожидаемся индексации
    for _ in range(30):
        status_response = await client.get(f"/api/files/{file_id}/status")
        if status_response.status_code == 200 and status_response.json() is True:
            break
        time.sleep(1)
    else:
        assert AssertionError(), "Индексация файла не завершилась вовремя"

    # Шаг 3: Отправляем запрос в /v1/chat/completions с shortcut
    request_data = {
        "file_id": file_id,
        "messages": [{"role": "user", "content": ""}],
        "snippet": "Text snippet",
        "action": "explain",
    }
    # Подготавливаем поток
    prepare_response = await client.post("/api/prepare_stream", json=request_data)

    stream_id = prepare_response.json()

    completion_params = {
        "method": "GET",
        "url": f"/api/v1/chat/completions?stream_id={stream_id}",
    }

    async with client.stream(**completion_params) as response:
        assert response.status_code == 200

    # Шаг 4: получаем историю
    response = await client.get(f"/api/history/{file_id}")
    assert response.status_code == 200

    history = response.json()
    assert len(history) == 2

    msg = history[0]
    assert msg["content"] == ""
    assert msg["is_user"] is True
    assert "timestamp" in msg

    assert msg["action"] == "explain"
    assert msg["snippet"] == "Text snippet"
