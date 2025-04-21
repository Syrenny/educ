import json
import time

import pytest


@pytest.mark.asyncio
async def test_chat_completions(
    client, 
    headers, 
    valid_pdf,
    upload_files_headers
    ):
    
    files = [('files', ('test.pdf', valid_pdf, 'application/pdf'))]
    response = await client.post(
        "/files",
        files=files,
        headers=upload_files_headers
    )

    filename = response.json()[0]["filename"]
    file_id = response.json()[0]["file_id"]
        
    assert response.status_code == 200
    assert filename == "test.pdf"

    indexing_done = False
    max_retries = 30
    retries = 0
    while not indexing_done and retries < max_retries:
        status_response = await client.get(
            f"/files/{file_id}/status",
            headers=headers
        )
        if status_response.status_code == 200:
            indexing_done = status_response.json()

        if not indexing_done:
            retries += 1
            time.sleep(1)
            
    print("Num retries:", retries)
            
    assert indexing_done, "File indexing did not complete in time"

    request_data = {
        "messages": [
            {
                "role": "user", 
                "content": "Декоратор field_validator всегда принимает один обязательный аргумент - название поля, которое необходимо валидировать. Второй аргумент, который предпочтительно указывать, mode."
            }
        ],
        "documents": [
            {
                "filename": filename,
                "file_id": file_id
            }
        ],
        "snippet": "",
        "action": "default"
    }

    completion_params = {
        "method": "POST",
        "url": "/v1/chat/completions",
        "json": request_data,
        "headers": headers
    }

    response_text = ""
    async with client.stream(**completion_params) as response:
        async for chunk in response.aiter_lines():
            if chunk:
                response_text += chunk + "\n"
                if chunk.startswith("data: "):
                    json_part = chunk[len("data: "):]
                    if json_part != "[DONE]":
                        parsed = json.loads(json_part)

                        assert "choices" in parsed
                        assert len(parsed["choices"]) > 0
                        assert "delta" in parsed["choices"][0]
                        assert "content" in parsed["choices"][0]["delta"]

    assert "data: [DONE]" in response_text


@pytest.mark.asyncio
@pytest.mark.parametrize("action, content, user_prompt", [
    ("translate", "Text fragment", "Please translate this paragraph"),
    ("explain", "Text fragment", "Что это значит?"),
    ("ask", "Text fragment", "Спроси что-нибудь")
])
async def test_chat_completions_with_shortcuts(
    client, headers, valid_pdf, upload_files_headers,
    action, content, user_prompt
):
    # Upload the PDF file
    files = [('files', ('test.pdf', valid_pdf, 'application/pdf'))]
    upload_response = await client.post(
        "/files",
        files=files,
        headers=upload_files_headers
    )
    assert upload_response.status_code == 200
    file_info = upload_response.json()[0]
    file_id = file_info["file_id"]
    filename = file_info["filename"]

    # Wait for file indexing to complete
    indexing_done = False
    retries = 0
    while not indexing_done and retries < 30:
        status_response = await client.get(f"/files/{file_id}/status", headers=headers)
        if status_response.status_code == 200:
            indexing_done = status_response.json()
        if not indexing_done:
            retries += 1
            time.sleep(1)
    assert indexing_done, "Indexing did not complete in time"

    # Prepare the chat request with shortcut
    request_data = {
        "messages": [{"role": "user", "content": user_prompt}],
        "documents": [{"filename": filename, "file_id": file_id}],
        "snippet": content,
        "action": action
    }

    completion_params = {
        "method": "POST",
        "url": "/v1/chat/completions",
        "json": request_data,
        "headers": headers
    }

    # Stream the response
    found_done = False
    async with client.stream(**completion_params) as response:
        assert response.status_code == 200
        async for chunk in response.aiter_lines():
            if chunk and chunk.startswith("data: "):
                json_part = chunk[len("data: "):]
                if json_part == "[DONE]":
                    found_done = True
                else:
                    parsed = json.loads(json_part)
                    assert "choices" in parsed
                    assert "delta" in parsed["choices"][0]
                    assert "content" in parsed["choices"][0]["delta"]

    assert found_done, "Streaming response did not include [DONE] marker"
