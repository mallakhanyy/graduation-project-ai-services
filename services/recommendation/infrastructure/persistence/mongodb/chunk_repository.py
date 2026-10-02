from core.interfaces.chunk_repository import ChunkRepository
from core.value_objects.document_chunk import DocumentChunk

from infrastructure.persistence.mongodb.mongodb_client import MongoDBClient
from shared.config import get_settings


class MongoChunkRepository(ChunkRepository):

    def __init__(self, mongodb_client: MongoDBClient):
        settings = get_settings()

        self.collection = mongodb_client.get_database()[
            settings.MONGODB_CHUNK_COLLECTION
        ]

    async def save(self, chunk: DocumentChunk) -> None:
        await self.collection.insert_one({
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
            "metadata": chunk.metadata,
            "chunk_order": chunk.chunk_order,
        })

    async def save_many(self, chunks: list[DocumentChunk]) -> None:
        documents = [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.metadata,
                "chunk_order": chunk.chunk_order,
            }
            for chunk in chunks
        ]

        if documents:
            await self.collection.insert_many(documents)

    async def get_by_document_id(
        self,
        document_id: str,
    ) -> list[DocumentChunk]:

        cursor = self.collection.find(
            {"metadata.document_id": document_id}
        )

        chunks = []

        async for document in cursor:
            chunks.append(
                DocumentChunk(
                    chunk_id=document["chunk_id"],
                    text=document["text"],
                    metadata=document["metadata"],
                    chunk_order=document["chunk_order"],
                )
            )

        return chunks