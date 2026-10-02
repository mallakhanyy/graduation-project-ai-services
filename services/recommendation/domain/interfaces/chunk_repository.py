from abc import ABC, abstractmethod

from core.value_objects.document_chunk import DocumentChunk


class ChunkRepository(ABC):

    @abstractmethod
    async def save(self, chunk: DocumentChunk) -> None:
        pass

    @abstractmethod
    async def save_many(self, chunks: list[DocumentChunk]) -> None:
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> list[DocumentChunk]:
        pass