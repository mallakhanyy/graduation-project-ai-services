import asyncio

from core.interfaces.embedding_service import EmbeddingService
from core.interfaces.vector_store import VectorStore
from core.value_objects.retrieved_chunk import RetrievedChunk


class RetrievalService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        top_k: int,
    ) -> list[RetrievedChunk]:

        query_embedding = await asyncio.to_thread(
            self.embedding_service.embed,
            query,
        )

        return await self.vector_store.search(
            embedding=query_embedding,
            top_k=top_k,
        )