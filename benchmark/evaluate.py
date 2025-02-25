from enum import Enum

import typer
from tqdm import tqdm
from ragas import (
    EvaluationDataset, 
    evaluate as ragas_evaluate
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether
from langchain_community.cache import SQLiteCache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.outputs import LLMResult, ChatGeneration


from benchmark.metrics import ragas_metrics
from benchmark.prepare import qasper, articles
from benchmark.configurations import BaseRAG
from benchmark.common import logger
from chat_backend.settings import settings


# As mentioned here https://github.com/explodinggradients/ragas/issues/1548 and here https://github.com/explodinggradients/ragas/pull/1728 need to realize custom is_finished funtion for LLAMA models
def llama_is_finished_parser(response: LLMResult) -> bool:
    is_finished_list = []

    for g in response.flatten():
        resp = g.generations[0][0]

        if resp.generation_info is not None:
            finish_reason = resp.generation_info.get("finish_reason")
            if finish_reason is not None:
                is_finished_list.append(finish_reason == "eos")
                continue

        if isinstance(resp, ChatGeneration) and resp.message is not None:
            metadata = resp.message.response_metadata
            if metadata.get("finish_reason"):
                is_finished_list.append(metadata["finish_reason"] == "eos")

        if not is_finished_list:
            is_finished_list.append(True)

    return all(is_finished_list)
    

app = typer.Typer()

# Limiting the rate of requests to the LLM to avoid hitting the rate limit.
together_rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)


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
        rate_limiter=together_rate_limiter,
    )
    embedder = HuggingFaceEmbeddings(
        model_name=settings.benchmark_embedding_model,
    )
    rag = BaseRAG.get(
        class_name=config_type,
        documents=articles,
        llm=llm,
        embedder=embedder
    )
    result = []
    for sample in tqdm(dataset.samples, desc="Inference samples"):
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
    
    # eval_llm = ChatOpenAI(
    #     model=settings.benchmark_llm_model_name,
    #     api_key=settings.benchmark_llm_api_key,
    #     base_url=settings.benchmark_llm_api_base,
    #     cache=SQLiteCache("./benchmark/openai_cache.db"),
    #     rate_limiter=together_rate_limiter,
    # )
    
    eval_llm = ChatTogether(
        model=settings.benchmark_llm_model_name,
        api_key=settings.benchmark_llm_api_key,
        cache=SQLiteCache("./benchmark/openai_cache.db"),
        rate_limiter=together_rate_limiter,
    )
    
    eval_embedder = HuggingFaceEmbeddings(
        model_name=settings.benchmark_embedding_model
    )
    
    # Inference questions to generate predictions and retrieve context
    dataset = inference(config, qasper)
    
    result = ragas_evaluate(
        dataset,
        metrics=ragas_metrics,
        llm=LangchainLLMWrapper(
            eval_llm, 
            is_finished_parser=llama_is_finished_parser
        ),
        embeddings=LangchainEmbeddingsWrapper(eval_embedder),
        raise_exceptions=True
    ).to_pandas()
    
    result.to_csv(f"./benchmark/results/{config}.csv")
    typer.echo(result)
    

if __name__ == "__main__":
    app()
