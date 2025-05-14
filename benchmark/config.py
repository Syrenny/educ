from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class ConfigType(str, Enum):
    llm = "llm"
    agentic = "agentic"
    system = "system"


class BenchmarkConfig(BaseModel):
    # LLM API configuration
    eval_llm_model_name: str = "google/gemini-2.5-pro-preview"

    results_path: Path = Path("./benchmark/results")


benchmark_config = BenchmarkConfig()
