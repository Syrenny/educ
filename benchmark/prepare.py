import ast
import random
from enum import Enum
from pathlib import Path

import numpy as np
from tqdm import tqdm
from datasets import load_dataset
from ragas import EvaluationDataset

from benchmark.common import logger
from chat_backend.settings import settings


class BenchmarkType(Enum):
    QASPER = "qasper"
    FRAMES = "frames"
    
    
# === Utils ===
def _load_arxiv_articles(paper_ids: list[str], output_dir: Path) -> list[str]:
    from langchain_community.retrievers import ArxivRetriever

    retriever = ArxivRetriever(
        load_max_docs=1,
        get_ful_documents=True,
    )
    result = []
    for paper_id in tqdm(paper_ids, desc="Downloading papers"):
        pdf_path = output_dir / f"{paper_id}.pdf"

        if pdf_path.exists():
            result.append(pdf_path.read_text())
            continue
        else:
            text = retriever.invoke(paper_id)[0].page_content
            pdf_path.write_text(text)
            result.append(text)
    return result


def _load_wiki_articles(wiki_links: list[str], output_dir: Path) -> list[str]:
    import requests
    from urllib.parse import urlparse, unquote
    
    result = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for link in tqdm(wiki_links, desc="Loading Wikipedia articles"):
        path = urlparse(link).path
        title = unquote(path.split('/')[-1])
        response = requests.get(
            url="https://en.wikipedia.org/w/api.php",
            params={
                'action': 'query',
                'prop': 'extracts',
                'titles': title,
                'rvprop': 'content',
                'format': 'json'
            }
        )
        if response.status_code != 200:
            logger.warning(f"{response.status_code} Could not find Wikipedia page for title {title} link {link}")
            continue
        
        file_path = output_dir / f"{title}.txt"
        
        if file_path.exists():
            result.append(file_path.read_text(encoding="utf-8"))
            continue

        data = response.json()
        text = ""
        for page_id, page in data["query"]["pages"].items():
            if page_id == '-1':
                logger.warning(f"Could not find Wikipedia page for title {title} link {link}")
            text += page["extract"] + "\n"
        file_path.write_text(text, encoding="utf-8")
        result.append(text)

    return result


def _parse_qasper(entry: dict, n: int) -> EvaluationDataset:
    extracted = []
    
    for sample in entry["qas"]:
        for question, answers in zip(sample["question"], sample["answers"]):
            for answer in answers["answer"]:
                extracted.append({
                    "user_input": question,
                    "reference": answer["free_form_answer"],
                })

    return EvaluationDataset.from_list(random.sample(extracted, n))


def _parse_frames(entry: dict, n: int) -> EvaluationDataset:
    extracted = []
    for prompt, answer in zip(entry["Prompt"], entry["Answer"]):
        extracted.append({
            "user_input": prompt,
            "reference": answer,
        })
    return EvaluationDataset.from_list(random.sample(extracted, n))
        
        
def _parse_wiki_links(links: list[str]):
    result = []
    for sample in links: 
        result.extend(ast.literal_eval(sample))
    return result

            
def prepare_benchmark(name: BenchmarkType) -> tuple[EvaluationDataset, list[str]]:
    if name == BenchmarkType.QASPER:
        # Download QASPER
        _ds = load_dataset(
            path="allenai/qasper",
            split="validation"
        )
        _paper_id = set(_ds["id"])

        # Make directory for articles
        output_dir = Path("./benchmark/data/raw/arxiv-papers")
        output_dir.mkdir(parents=True, exist_ok=True)

        articles = _load_arxiv_articles(_paper_id, output_dir)
        # Parse QASPER and get N samples for benchmarking
        logger.info(f"Articles have been loaded, total number: {len(articles)}")
        
        return _parse_qasper(_ds, settings.benchmark_n_samples), articles
    
    elif name == BenchmarkType.FRAMES:        
        # Download FRAMES
        _ds = load_dataset(
            path="google/frames-benchmark",
            split="test"
        ).shuffle(seed=42).select(range(settings.benchmark_n_samples * 2))
        
        _wiki_links = set(_parse_wiki_links(_ds["wiki_links"]))

        # Make directory for wiki articles
        output_dir = Path("./benchmark/data/raw/wiki")
        output_dir.mkdir(parents=True, exist_ok=True)

        articles = _load_wiki_articles(_wiki_links, output_dir)
        # Parse QASPER and get N samples for benchmarking
        logger.info(
            f"Articles have been loaded, total number: {len(articles)}")
        return _parse_frames(_ds, settings.benchmark_n_samples), articles


