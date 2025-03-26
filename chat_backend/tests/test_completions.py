import json
import contextlib

import pytest
from fastapi.testclient import TestClient

from chat_backend.main import app
from chat_backend.settings import settings


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
        
        
@pytest.fixture
def token(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    response = client.post("/login_user", json=user_data)
    response_data = response.json()
    return response_data['token']


def test_chat_completions(client, token):
    # === Send completion ===
    
    request_data = {
        "messages": [
            {"role": "user", "content": "Декоратор field_validator всегда принимает один обязательный аргумент - название поля, которое необходимо валидировать. Второй аргумент, который предпочтительно указывать, mode."}
        ],
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
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
            print("Chunk", chunk)
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
