from smolagents import OpenAIServerModel

from chat_backend.settings import settings


llm = OpenAIServerModel(
    model_id=settings.llm_model_name,
    api_base=settings.llm_api_base,
    api_key=settings.llm_api_key,
)
