from dataclasses import dataclass, field
import typing as t

from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    AnswerCorrectness,
)
from ragas.metrics.base import (
    Metric,
    SingleTurnMetric,
    MetricType,
    SingleTurnSample,
)
from ragas.run_config import RunConfig
from bert_score import BERTScorer
from langchain_core.callbacks import Callbacks


@dataclass
class BertScore(SingleTurnMetric):
    name: str = "bert_score"
    _required_columns: t.Dict[MetricType, t.Set[str]] = field(
        default_factory=lambda: {
            MetricType.SINGLE_TURN: {
                "reference", 
                "response"
            }
        }
    )
    
    def init(self, run_config: RunConfig):
        self.bert_scorer = BERTScorer(
            lang="ru",
            device="cuda"
        )

        
    async def _single_turn_ascore(
        self,
        sample: SingleTurnSample,
        callbacks: Callbacks = None,
    ) -> float:
        return float(self.bert_scorer.score(
            cands=sample.response,
            refs=sample.reference
        )[-1].mean())
        

ragas_metrics = [
    # Faithfulness(),
    # ResponseRelevancy(),
    AnswerCorrectness(),
    # BertScore()
]


