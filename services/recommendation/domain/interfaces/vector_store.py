from abc import ABC, abstractmethod

from core.value_objects.document_chunk import DocumentChunk
from core.value_objects.retrieved_chunk import RetrievedChunk


class VectorStore(ABC):

    @abstractmethod
    async def add(self, chunks: list[DocumentChunk], embeddings: list[list[float]],)-> None:
        pass

    @abstractmethod
    async def search(self, embedding: list[float], top_k: int,)-> list[RetrievedChunk]:
        pass