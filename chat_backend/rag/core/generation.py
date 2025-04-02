from typing import Iterator

from ..utils.llm import get_langchain_llm


class Generator:
    prompt_template = """
    You are an expert in scientific research. Answer the following question on a scientific topic using the provided documents.
    Question: {query}
    Documents: {documents}
    """

    def __init__(self):
        self.llm = get_langchain_llm()

    def __generate_stream(self,
                  query: str,
                  context: list[str]
                  ) -> str:
        prompt = self.prompt_template.format(
            query=query, documents='\n'.join(context))

        return self.llm.stream(prompt)

    def __call__(self,
                 query: str,
                 context: list[str]
                 ) -> Iterator[str]:
        for chunk in self.__generate_stream(query, context):
            yield chunk.text()
