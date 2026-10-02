import asyncio
from pathlib import Path

from infrastructure.storage.http_audio_downloader import (
    HttpAudioDownloader,
)


AUDIO_URL = "http://localhost:9000/asr-audio/9_256_cropped.flac?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20260730%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260730T014625Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=4701eaa2b85baced18f6049dc9e244fa9fd1508da2405ac57e8f1bede8d1d847"
DESTINATION = "/tmp/asr_downloader_test.flac"
MAX_SIZE_BYTES = 25 * 1024 * 1024


async def main():

    downloader = HttpAudioDownloader()

    path = await downloader.download(
        audio_url=AUDIO_URL,
        destination_path=DESTINATION,
        max_size_bytes=MAX_SIZE_BYTES,
    )

    file_path = Path(path)

    print(f"Downloaded to: {file_path}")
    print(f"File exists: {file_path.exists()}")
    print(f"File size: {file_path.stat().st_size} bytes")


if __name__ == "__main__":
    asyncio.run(main())