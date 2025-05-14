from pathlib import Path

from pydantic import BaseModel


class TrainingLAConfig(BaseModel):
    # LLM API configuration
    eval_llm_model_name: str = "google/gemini-2.5-pro-preview"

    results_path: Path = Path("./benchmark/results")

    # Model
    checkpoint: str = "cointegrated/rubert-tiny2"


config = TrainingLAConfig()
