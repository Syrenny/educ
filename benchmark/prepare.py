import random
from pathlib import Path

from tqdm import tqdm
from datasets import load_dataset
from ragas import EvaluationDataset
from langchain_community.retrievers import ArxivRetriever

from benchmark.common import logger
from chat_backend.settings import settings


def prepare_qasper(entry: dict, n: int) -> EvaluationDataset:
    extracted = []
    
    for sample in entry["qas"]:
        for question, answers in zip(sample["question"], sample["answers"]):
            for answer in answers["answer"]:
                extracted.append({
                    "user_input": question,
                    "reference": answer["free_form_answer"],
                })

    return EvaluationDataset.from_list(random.sample(extracted, n))
        
        
def load_articles(paper_ids: list[str], output_dir: Path) -> list[str]:
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
            
    
# Download QASPER
_ds = load_dataset(
    path="allenai/qasper",
    split="validation"
)
_paper_id = set(_ds["id"])

# Prepare directory for articles
output_dir = Path("./benchmark/data/raw/arxiv-papers")
output_dir.mkdir(parents=True, exist_ok=True)

# Parse QASPER and get N samples for benchmarking
qasper = prepare_qasper(_ds, settings.benchmark_n_samples)
logger.info(f"QASPER has been parsed, got {settings.benchmark_n_samples} samples for testing")

# Load articles for indexing
articles = load_articles(_paper_id, output_dir)
logger.info(f"Articles have been loaded, total number: {len(articles)}")


