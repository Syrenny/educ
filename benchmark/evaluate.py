from pathlib import Path

import typer
from ragas import EvaluationDataset
from ragas import evaluate as ragas_evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerCorrectness,
    ContextPrecision,
    Faithfulness,
    ResponseRelevancy,
)
from tqdm import tqdm

from benchmark.config import ConfigType, benchmark_config
from benchmark.configurations import BaseRAG
from benchmark.dataset import load_dataset_from_files
from server.utils.llm import get_langchain_embeddings, get_langchain_llm

ragas_metrics = [
    ContextPrecision(),
    Faithfulness(),
    ResponseRelevancy(),
    AnswerCorrectness(),
]

app = typer.Typer()


def inference(
    config: ConfigType,
    dataset: EvaluationDataset,
    articles: list[str],
) -> EvaluationDataset:
    rag = BaseRAG.get(class_name=config, documents=articles)
    result = []
    for sample in tqdm(dataset.samples, desc="Inference samples"):
        response, context = rag(sample.user_input)
        result.append(
            {
                "user_input": sample.user_input,
                "retrieved_contexts": context,
                "response": response,
                "reference": sample.reference,
            }
        )

    return EvaluationDataset.from_list(result)


@app.command()
def evaluate(
    config: ConfigType = typer.Option("--config"),
    checkpoint: Path = typer.Option("--checkpoint"),
):
    """App for evaluating selected qa-system configuration."""

    # Preparing dataset
    dataset, articles = load_dataset_from_files(checkpoint)

    typer.echo(f"Evaluating {config}")

    # Inference questions to generate predictions and retrieve context
    dataset = inference(config=config, dataset=dataset, articles=articles)

    # Save dataset for checking
    dataset.to_jsonl("./benchmark/data/transformed/inference.jsonl")

    eval_llm = get_langchain_llm(benchmark_config.eval_llm_model_name)
    eval_embedder = get_langchain_embeddings()

    result = ragas_evaluate(
        dataset,
        metrics=ragas_metrics,
        llm=LangchainLLMWrapper(
            eval_llm,
        ),
        embeddings=LangchainEmbeddingsWrapper(eval_embedder),
        raise_exceptions=True,
    )
    result.to_pandas().to_csv(f"./benchmark/results/{config.name}.csv")
    typer.echo(result)


if __name__ == "__main__":
    app()
