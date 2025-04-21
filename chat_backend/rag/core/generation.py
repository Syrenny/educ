from typing import AsyncGenerator

from chat_backend.utils.llm import get_langchain_llm
from chat_backend.models import Action


class Generator:
    __default = """
    You are an expert in scientific research. Answer the following question on a scientific topic using the provided documents.
    Question: {query}
    Documents: 
    {documents}
    """

    __translate = """
    Переведи следующий текст на русский язык, сохраняя его смысл и стиль:
    Текст: 
    {snippet}
    """

    __explain = """
    На основе предоставленных ниже фрагментов документов объясни значение отрезка текста. Убедись, что объяснение будет максимально точным, с учетом контекста и фактов из документов. Ответ предоставь на русском языке:

    Отрезок текста: 
    {snippet}

    Документы: 
    {documents}
    """

    __ask = """
    Ответь на следующий вопрос, основываясь на приведенном отрезке текста и предоставленных ниже фрагментах документов. Используй только информацию из документов для составления точного ответа на вопрос. Ответ предоставь на русском языке.

    Вопрос: {query}
    Отрезок текста: 
    {snippet}

    Документы:
    {documents}
    """

    def __init__(self, action: Action, snippet: str | None):
        self.llm = get_langchain_llm()
        self.action = action
        self.snippet = snippet

    def make_prompt(self, query: str, context: list[str]):
        if self.action == Action.default:
            return self.__default.format(
                query=query,
                documents='\n'.join(context)
            )
        elif self.action == Action.translate:
            return self.__translate.format(
                snippet=self.snippet
            )
        elif self.action == Action.explain:
            return self.__explain.format(
                snippet=self.snippet,
                documents='\n'.join(context)
            )
        elif self.action == Action.ask:
            return self.__ask.format(
                query=query,
                snippet=self.snippet,
                documents='\n'.join(context)
            )
        else:
            raise ValueError("None of action selected")

    async def __generate_stream(self,
                                query: str,
                                context: list[str]
                                ) -> AsyncGenerator[str, None]:
        prompt = self.make_prompt(query, context)

        async for ai_message in self.llm.astream(prompt):
            yield ai_message.text()

    def __call__(self,
                 query: str,
                 context: list[str]
                 ) -> AsyncGenerator[str, None]:
        return self.__generate_stream(query, context)
