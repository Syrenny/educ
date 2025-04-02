import json


def test_chat_completions(
    client, 
    headers, 
    valid_pdf,
    upload_files_headers
    ):
    # === Send completion ===
    
    files = [('files', ('test.pdf', valid_pdf, 'application/pdf'))]
    response = client.post(
        "/files",
        files=files,
        headers=upload_files_headers
    )

    filename = response.json()[0]["filename"]
    file_id = response.json()[0]["file_id"]
    
    assert response.status_code == 200
    assert filename == "test.pdf"
    

    request_data = {
        "messages": [
            {
                "role": "user", 
                "content": "Декоратор field_validator всегда принимает один обязательный аргумент - название поля, которое необходимо валидировать. Второй аргумент, который предпочтительно указывать, mode."
            }
        ],
        "documents": [
            {
                filename: file_id
            }
        ]
    }

    completion_params = {
        "method": "post",
        "url": "/v1/chat/completions",
        "json": request_data,
        "headers": headers
    }

    response_text = ""
    with client.stream(**completion_params) as response:
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk
                response_text += decoded_chunk + "\n"

                if decoded_chunk.startswith("data: "):
                    json_part = decoded_chunk[len("data: "):]
                    if json_part != "[DONE]":
                        parsed = json.loads(json_part)

                        assert "choices" in parsed
                        assert len(parsed["choices"]) > 0
                        assert "delta" in parsed["choices"][0]
                        assert "content" in parsed["choices"][0]["delta"]


    assert "data: [DONE]" in response_text
