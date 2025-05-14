import ast
import json
import random
import string
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import typer
from datasets import load_dataset
from loguru import logger
from ragas import EvaluationDataset
from tqdm import tqdm


def _load_wiki_articles(wiki_links: list[str], output_dir: Path) -> list[str]:
    result = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for link in tqdm(wiki_links, desc="Loading Wikipedia articles"):
        path = urlparse(link).path
        title = unquote(path.split("/")[-1])
        response = requests.get(
            url="https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "titles": title,
                "rvprop": "content",
                "format": "json",
                "explaintext": "true",
            },
        )
        if response.status_code != 200:
            logger.warning(
                f"{response.status_code} Could not find Wikipedia page for title {title} link {link}"
            )
            continue

        file_path = output_dir / f"{title}.txt"

        if file_path.exists():
            result.append(file_path.read_text(encoding="utf-8"))
            continue

        data = response.json()
        text = ""
        for page_id, page in data["query"]["pages"].items():
            if page_id == "-1":
                logger.warning(
                    f"Could not find Wikipedia page for title {title} link {link}"
                )
            text += page["extract"] + "\n"
        file_path.write_text(text, encoding="utf-8")
        result.append(text)

    return result


def _parse_frames(entry: dict, n: int) -> EvaluationDataset:
    extracted = []
    for prompt, answer in zip(entry["Prompt"], entry["Answer"], strict=False):
        extracted.append(
            {
                "user_input": prompt,
                "reference": answer,
            }
        )
    return EvaluationDataset.from_list(random.sample(extracted, n))


def _parse_wiki_links(links: list[str]):
    result = []
    for sample in links:
        result.extend(ast.literal_eval(sample))
    return result


def _prepare_dataset() -> tuple[EvaluationDataset, list[str]]:
    # Download FRAMES
    n_samples = 50
    _ds = (
        load_dataset(path="google/frames-benchmark", split="test")
        .shuffle(seed=42)
        .select(range(n_samples * 2))
    )

    _wiki_links = list(set(_parse_wiki_links(_ds["wiki_links"])))

    # Make directory for wiki articles
    output_dir = Path("./benchmark/data/raw/wiki")
    output_dir.mkdir(parents=True, exist_ok=True)

    articles = _load_wiki_articles(_wiki_links, output_dir)
    logger.info(f"Articles have been loaded, total number: {len(articles)}")
    return _parse_frames(_ds, n_samples), articles


def _save_dataset(dataset: EvaluationDataset, articles: list[str]) -> Path:
    base_dir = "./benchmark/data/transformed/datasets"

    # Creating unique checkpoint directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    random_part = "".join(random.choices(string.ascii_letters + string.digits, k=6))

    _dir = Path(base_dir) / f"FRAMES_{timestamp}_{random_part}"
    _dir.mkdir(parents=True, exist_ok=True)

    # Save dataset
    dataset.to_jsonl(_dir / "dataset.json")

    with (_dir / "articles.json").open(mode="w") as file:
        json.dump(articles, file, indent=4)

    return _dir


def load_dataset_from_files(checkpoint: Path) -> tuple[EvaluationDataset, list[str]]:
    dataset = EvaluationDataset.from_jsonl(checkpoint / "dataset.json")
    with (checkpoint / "articles.json").open(mode="r") as file:
        articles = json.load(file)

    logger.info(f"Dataset has been loaded from {checkpoint}")

    return dataset, articles


app = typer.Typer()


@app.command()
def prepare():
    """App for preparing selected dataset."""
    dataset, articles = _prepare_dataset()

    dataset_path = _save_dataset(dataset, articles)
    logger.info(f"Dataset checkpoint created at: {dataset_path}")


if __name__ == "__main__":
    app()
