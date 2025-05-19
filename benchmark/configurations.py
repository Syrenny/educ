import asyncio
from abc import ABC, abstractmethod

import numpy as np
from smolagents import LogLevel, Tool, ToolCallingAgent
from tqdm import tqdm

from benchmark.config import ConfigType
from benchmark.utils import Asphodel
from server.rag.core.generation import Action, Generator
from server.rag.core.indexing import SemanticChunker
from server.utils.llm import get_langchain_embeddings, get_langchain_llm


class BaseRAG(ABC, Asphodel):
    prompt_template = ""

    def __init__(self, documents: list[str]):
        self.documents = documents
        self.llm = get_langchain_llm()
        self.embedder = get_langchain_embeddings()

    @abstractmethod
    def retrieve(self, query: str) -> list[str]: ...

    @abstractmethod
    def __call__(self, query: str) -> tuple[str, list[str]]: ...


@BaseRAG.register(ConfigType.llm)
class JustLLM(BaseRAG):
    def __init__(self, documents: list[str]):
        self.documents = documents
        self.llm = get_langchain_llm()
        self.embedder = get_langchain_embeddings()

    def retrieve(self, query: str) -> list[str]:
        return []

    def __call__(self, query: str) -> tuple[str, list[str]]:
        return self.llm.invoke(query).text(), []


@BaseRAG.register(ConfigType.system)
class SystemRAG(BaseRAG):
    def __init__(self, documents):
        super().__init__(documents)
        self.generator = Generator(action=Action.default, snippet=None)
        chunker = SemanticChunker()

        self.chunks = []
        for document in tqdm(documents, desc="Documents indexation"):
            self.chunks.extend(chunker(document))
        self.embeddings = self.embedder.embed_documents(self.chunks)

    def l2_dist(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def retrieve(self, query: str) -> list[str]:
        query_embedding = self.embedder.embed_query(query)
        distances = [
            self.l2_dist(query_embedding, doc_emb) for doc_emb in self.embeddings
        ]

        return [self.chunks[i] for i in np.argsort(distances)[:5]]

    async def _get_answer(self, query: str, context: list[str]) -> str:
        chunks = []
        async for chunk in self.generator(query=query, context=context):
            chunks.append(chunk)
        return "".join(chunks)

    def __call__(self, query: str) -> tuple[str, list[str]]:
        context = self.retrieve(query)
        answer = asyncio.run(self._get_answer(query, context))

        return answer, context


class RetrieverTool(Tool):
    name = "retriever"
    description = """
    Uses semantic search to retrieve the parts of wiki that could be most relevant to answer your query."""
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to perform. This should be semantically close to your target documents. Use the affirmative form rather than a question.",
        }
    }
    output_type = "string"

    def __init__(self, rag: BaseRAG, **kwargs):
        super().__init__(**kwargs)
        self.rag = rag

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"

        docs = self.rag.retrieve(
            query,
        )
        return "\nRetrieved documents:\n" + "".join(
            [f"\n\n===== Document {str(i)} =====\n" + doc for i, doc in enumerate(docs)]
        )


@BaseRAG.register(ConfigType.agentic)
class AgenticRAG(BaseRAG):
    def __init__(self, documents):
        super().__init__(documents)
        rag = BaseRAG.get(class_name="system", documents=documents)
        retriever_tool = RetrieverTool(rag=rag)
        self.agent = ToolCallingAgent(
            tools=[retriever_tool],
            model=self.llm,
            name="Agentic RAG",
            description="Agentic RAG is a system, where LLM can decide whether to use retriever or not.",
            verbosity_level=LogLevel.ERROR,
        )

    def retrieve(self, query: str) -> list[str]:
        return []

    def __call__(self, query: str) -> tuple[str, list[str]]:
        context = [""]
        # source: https://github.com/huggingface/smolagents/blob/main/src/smolagents/gradio_ui.py
        for step_log in self.agent.run(query, stream=True):
            if hasattr(step_log, "observations") and (
                step_log.observations is not None and step_log.observations.strip()
            ):
                context[0] = step_log.observations

        return step_log, context
