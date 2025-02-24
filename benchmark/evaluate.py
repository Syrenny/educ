from enum import Enum

import typer
from ragas import (
    EvaluationDataset, 
    evaluate as ragas_evaluate
)

from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.cache import SQLiteCache

from benchmark.metrics import ragas_metrics
from benchmark.prepare import qasper, articles
from benchmark.configurations import BaseRAG
from benchmark.common import logger
from chat_backend.settings import settings


app = typer.Typer()


class ConfigType(str, Enum):
    """Enum for configuration types."""
    llm = "llm"
    default_rag = "default-rag"
    agentic_rag = "agentic-rag"


def inference(
    config_type: ConfigType, 
    dataset: EvaluationDataset
    ) -> EvaluationDataset:
    llm = ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        # Always a good idea to use Cache
        cache=SQLiteCache("./benchmark/openai_cache.db"),

    )
    embedder = HuggingFaceEmbeddings(
        model_name=settings.benchmark_embedding_model,
    )
    rag = BaseRAG.get(
        config_type,
        documents=articles,
        llm=llm,
        embedder=embedder
    )
    result = []
    for sample in dataset.samples:
        response, context = rag(sample.user_input)
        result.append(
            {
                "user_input": sample.user_input,
                "retrieved_contexts": context,
                "response": response,
                "reference": sample.reference
            }
        )
    return EvaluationDataset.from_list(result)
    
        

@app.command()
def evaluate(config: ConfigType):
    """App for evaluating selected qa-system configuration."""
    typer.echo(f"Evaluating {config}")
    
    eval_llm = LangchainEmbeddingsWrapper(ChatOpenAI(
        model=settings.benchmark_llm_model_name,
        api_key=settings.benchmark_llm_api_key,
        base_url=settings.benchmark_llm_api_base,
        cache=SQLiteCache("./benchmark/openai_cache.db"),
    ))
    
    eval_embedder = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(
        model_name=settings.benchmark_embedding_model
    ))
    
    # Inference questions to generate predictions and retrieve context
    dataset = inference(config, qasper)
    
    result = ragas_evaluate(
        dataset,
        metrics=ragas_metrics,
        llm=eval_llm,
        embeddings=eval_embedder
    )
    
    logger.info("Result metrics:", result)
    typer.echo(result)
    

if __name__ == "__main__":
    app()
