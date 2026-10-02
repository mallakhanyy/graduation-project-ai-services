import asyncio

from application.services.document_ingestion_service import (
    DocumentIngestionService,
)

from infrastructure.storage.minio_storage import MinIOStorage
from infrastructure.document_processing.pdf_loader import PDFLoader
from infrastructure.document_processing.chunker import Chunker
from infrastructure.persistence.mongodb.mongodb_client import (
    MongoDBClient,
)
from infrastructure.persistence.mongodb.chunk_repository import (
    MongoChunkRepository,
)
from infrastructure.embeddings.bge_m3_embedding import (
    BGEM3EmbeddingService,
)
from infrastructure.persistence.qdrant.qdrant_client import (
    QdrantClient,
)
from infrastructure.persistence.qdrant.vector_store import (
    QdrantVectorStore,
)

from shared.config import get_settings


async def main():

    settings = get_settings()

    # MinIO
    storage = MinIOStorage()

    # PDF loader
    loader = PDFLoader()

    # Chunker
    chunker = Chunker(
        chunk_size=settings.FILE_DEFAULT_CHUNK_SIZE,
        chunk_overlap=settings.FILE_CHUNK_OVERLAP,
    )

    # MongoDB
    mongodb_client = MongoDBClient()

    chunk_repository = MongoChunkRepository(
        mongodb_client=mongodb_client,
    )

    # BGE-M3
    embedding_service = BGEM3EmbeddingService()

    # Qdrant
    qdrant_client = QdrantClient()

    vector_store = QdrantVectorStore(
        qdrant_client=qdrant_client,
        embedding_service=embedding_service,
    )

    # Ingestion service
    ingestion_service = DocumentIngestionService(
        storage=storage,
        loader=loader,
        chunker=chunker,
        chunk_repository=chunk_repository,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # Use one PDF that already exists in MinIO
    object_key = "ICARDA_Rainwater Harvesting Design Manual_FINAL.pdf"

    await ingestion_service.ingest(object_key)

    # Cleanup
    mongodb_client.close()
    qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(main())