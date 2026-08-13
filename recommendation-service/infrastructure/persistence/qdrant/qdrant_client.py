from qdrant_client import QdrantClient as QdrantSDKClient

from shared.config import get_settings


class QdrantClient:

    def __init__(self):
        settings = get_settings()

        self.client = QdrantSDKClient(
            url=settings.QDRANT_URL,
            timeout=60.0,
        )

    def get_client(self) -> QdrantSDKClient:
        return self.client

    def close(self) -> None:
        self.client.close()