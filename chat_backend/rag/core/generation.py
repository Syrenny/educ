from typing import AsyncGenerator

from loguru import logger

from ..utils.llm import get_langchain_llm
from chat_backend.models import ShortcutModel


class Generator:
    __default = """
    You are an expert in scientific research. Answer the following question on a scientific topic using the provided documents.
    Question: {query}
    Documents: 
    {documents}
    """
    
    __translate = """
    Переведи следующий текст на русский язык, сохраняя его смысл и стиль:
    Текст: {text}
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

    def __init__(self, shortcut: ShortcutModel | None):
        self.llm = get_langchain_llm()
        self.shortcut = shortcut
        
    def make_prompt(self, query: str, context: list[str]):
        logger.debug("Shortcut", self.shortcut)
        if self.shortcut is None:
            return self.__default.format(
                query=query,
                documents='\n'.join(context)
            )
        elif self.shortcut.action == "translate":
            return self.__translate.format(
                text=query
            )
        elif self.shortcut.action == "explain":
            return self.__explain.format(
                snippet=self.shortcut.content, 
                documents='\n'.join(context)
            )
        elif self.shortcut.action == "ask":
            return self.__ask.format(
                query=query, 
                snippet=self.shortcut.content,
                documents='\n'.join(context)
            )
        else:
            return self.__default.format(
                query=query,
                documents='\n'.join(context)
            )
            

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
