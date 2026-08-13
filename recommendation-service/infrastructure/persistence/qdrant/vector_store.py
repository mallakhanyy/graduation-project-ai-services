from qdrant_client.models import Distance, PointStruct, VectorParams
from uuid import uuid5, NAMESPACE_URL

from core.interfaces.embedding_service import EmbeddingService
from core.interfaces.vector_store import VectorStore
from core.value_objects.document_chunk import DocumentChunk
from core.value_objects.retrieved_chunk import RetrievedChunk
from core.enums.vector_distance import VectorDistance

from infrastructure.persistence.qdrant.qdrant_client import QdrantClient
from shared.config import get_settings


class QdrantVectorStore(VectorStore):

    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_service: EmbeddingService,
    ):
        settings = get_settings()

        self.client = qdrant_client.get_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

        self.distance = self._get_distance(
            settings.QDRANT_DISTANCE
        )

        self.vector_size = embedding_service.dimension

        self._ensure_collection()

    def _get_distance(
        self,
        distance: VectorDistance,
    ) -> Distance:

        if distance == VectorDistance.COSINE:
            return Distance.COSINE

        if distance == VectorDistance.DOT:
            return Distance.DOT

        if distance == VectorDistance.EUCLID:
            return Distance.EUCLID

        raise ValueError(
            f"Unsupported Qdrant distance: {distance}"
        )

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections()

        exists = any(
            collection.name == self.collection_name
            for collection in collections.collections
        )

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance,
                ),
            )

    async def add(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings."
            )

        points = [
            PointStruct(
                id=str(uuid5(NAMESPACE_URL, chunk.chunk_id)),
                vector=embedding,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                    "chunk_order": chunk.chunk_order,
                },
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    async def search(
        self,
        embedding: list[float],
        top_k: int,
    ) -> list[RetrievedChunk]:

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=top_k,
        )

        return [
            RetrievedChunk(
                chunk_id=result.payload["chunk_id"],
                text=result.payload["text"],
                metadata=result.payload["metadata"],
                score=result.score,
            )
            for result in results.points
        ]