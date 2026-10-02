from abc import ABC, abstractmethod


class FileStorage(ABC):

    @abstractmethod
    def download(self, object_key: str) -> bytes:
        pass

    @abstractmethod
    def list_objects(self) -> list[str]:
        pass