from typing import AsyncGenerator

from ..utils.llm import get_langchain_llm


class Generator:
    prompt_template = """
    You are an expert in scientific research. Answer the following question on a scientific topic using the provided documents.
    Question: {query}
    Documents: {documents}
    """

    def __init__(self):
        self.llm = get_langchain_llm()

    async def __generate_stream(self,
                  query: str,
                  context: list[str]
                  ) -> AsyncGenerator[str, None]:
        prompt = self.prompt_template.format(
            query=query, documents='\n'.join(context))

        async for ai_message in self.llm.astream(prompt):
            yield ai_message.text()

    def __call__(self,
                query: str,
                context: list[str]
                ) -> AsyncGenerator[str, None]:
        return self.__generate_stream(query, context)
