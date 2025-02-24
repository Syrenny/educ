from dataclasses import dataclass, field
import typing as t

from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    AnswerCorrectness,
)
from ragas.metrics.base import (
    MetricWithEmbeddings,
    MetricType,
    SingleTurnSample,
)
from bert_score import BERTScorer
from langchain_core.callbacks import Callbacks


@dataclass
class BertScore(MetricWithEmbeddings):
    name: str = "bert_score"
    _required_columns: t.Dict[MetricType, t.Set[str]] = field(
        default_factory=lambda: {
            MetricType.SINGLE_TURN: {"reference", "response"}
        }
    )
    
    def single_turn_score(
        self,
        sample: SingleTurnSample,
        callbacks: Callbacks = None,
    ) -> float:
        bert_scorer = BERTScorer(
            lang="ru",
            device="cuda"
        )
        return float(bert_scorer.score(
            cands=list(sample.response),
            refs=list(sample.reference)
        )[-1].mean())
        

ragas_metrics = [
    Faithfulness,
    ResponseRelevancy,
    AnswerCorrectness,
    BertScore
]


