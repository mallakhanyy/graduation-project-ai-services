from abc import ABC, abstractmethod


class AudioDownloader(ABC):

    @abstractmethod
    async def download(
        self,
        audio_url: str,
        destination_path: str,
        max_size_bytes: int,
    ) -> str:
        pass