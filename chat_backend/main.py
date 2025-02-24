# source: https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/api_server.py#L25

from fastapi import FastAPI

from chat_backend.api.completions import router as completions_router
from chat_backend.api.files import router as files_router


app = FastAPI()
app.include_router(completions_router)
app.include_router(files_router)

