from abc import ABC, abstractmethod

from core.value_objects.document_chunk import DocumentChunk
from core.value_objects.loaded_page import LoadedPage


class Chunker(ABC):

    @abstractmethod
    def chunk(
        self,
        pages: list[LoadedPage],
        document_id: str,
    ) -> list[DocumentChunk]:
        pass