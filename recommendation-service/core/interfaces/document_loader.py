from abc import ABC, abstractmethod

from core.value_objects.loaded_page import LoadedPage


class DocumentLoader(ABC):

    @abstractmethod
    def load(self, file_bytes: bytes) -> list[LoadedPage]:
        pass