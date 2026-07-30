import httpx

from core.interfaces.audio_downloader import AudioDownloader
from shared.logger import logger


class HttpAudioDownloader(AudioDownloader):

    async def download(
        self,
        audio_url: str,
        destination_path: str,
        max_size_bytes: int,
    ) -> str:

        logger.info(
            f"Downloading audio from remote storage to: {destination_path}"
        )

        total_size = 0

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=None,
        ) as client:

            async with client.stream(
                "GET",
                audio_url,
            ) as response:

                response.raise_for_status()

                with open(destination_path, "wb") as audio_file:

                    async for chunk in response.aiter_bytes():

                        total_size += len(chunk)

                        if total_size > max_size_bytes:
                            raise ValueError(
                                "Audio file exceeds the maximum allowed size."
                            )

                        audio_file.write(chunk)

        logger.info(
            f"Audio downloaded successfully: {destination_path}"
        )

        return destination_path