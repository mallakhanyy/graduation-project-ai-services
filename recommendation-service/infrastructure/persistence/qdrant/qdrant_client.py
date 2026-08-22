from qdrant_client import AsyncQdrantClient

from shared.config import get_settings


class QdrantClient:

    def __init__(self):
        settings = get_settings()

        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            timeout=60.0,
        )

    def get_client(self) -> AsyncQdrantClient:
        return self.client

    async def close(self) -> None:
        await self.client.close()