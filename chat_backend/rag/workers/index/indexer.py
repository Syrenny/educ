from abc import ABC, abstractmethod

from .chunking import BaseChunker
from chat_backend.settings import settings


class BaseIndexer(ABC):
    def __init__(self):
        super().__init__()
        self.chunker = BaseChunker.get(
            class_name=settings.chunker_name
        )
        
    @abstractmethod
    def _chunking(document: str) -> list[str]:
        pass
    
    @abstractmethod
    def __call__(document: str):
        pass
    
    
class Indexer(BaseIndexer):
    @abstractmethod
    def _chunking():
        pass
