
from pathlib import Path

import arxiv
import pandas as pd
from datasets import load_dataset
from ragas import EvaluationDataset
from huggingface_hub import hf_hub_download

from chat_backend.settings import settings
from benchmark.common import logger


def prepare_qasper(entry) -> EvaluationDataset:
    extracted = []
    
    for question, answers in zip(entry["qas"]["question"], entry["qas"]["answers"]):
        for answer in answers["answer"]:
            extracted.append({
                "user_input": question,
                "reference": answer["free_form_answer"],
            })

    return EvaluationDataset.from_list(extracted)


def download_paper(paper_id, output_dir):
    search = arxiv.Search(id_list=[paper_id])

    for result in search.results():
        pdf_path = output_dir / f"{paper_id}.pdf"

        if pdf_path.exists():
            return pdf_path

        result.download_pdf(str(pdf_path))
        return pdf_path
        
        
def load_articles(paper_ids):
    for paper_id in paper_ids:
        try:
            download_paper(paper_id)
        except Exception as e:
            logger.error(f"❌ Error occured when loading {paper_id}: {e}")
    

# Download embedding model
hf_hub_download(
    repo_id=settings.benchmark_embedding_model
)
    
# Download QASPER
_ds = load_dataset("allenai/qasper")
_paper_id = set(_ds["id"])

# Prepare directory for articles
output_dir = Path("./benchmark/arxiv_papers")
output_dir.mkdir(parents=True, exist_ok=True)

# Parse QASPER
qasper = prepare_qasper(_ds)
articles = load_articles(_paper_id)

logger.info(f"Articles have been loaded, total number: {len(articles)}")


