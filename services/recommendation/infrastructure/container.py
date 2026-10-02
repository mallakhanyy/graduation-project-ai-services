from shared.config import get_settings

from application.services.context_builder_service import ContextBuilderService
from application.services.document_ingestion_service import DocumentIngestionService
from application.services.prompt_builder_service import PromptBuilderService
from application.services.recommendation_service import RecommendationService
from application.services.retrieval_service import RetrievalService

from infrastructure.document_processing.chunker import Chunker
from infrastructure.document_processing.pdf_loader import PDFLoader
from infrastructure.embeddings.bge_m3_embedding import BGEM3EmbeddingService
from infrastructure.llm.qwen3_llm_service import Qwen3LLMService
from infrastructure.persistence.mongodb.chunk_repository import MongoChunkRepository
from infrastructure.persistence.mongodb.mongodb_client import MongoDBClient
from infrastructure.persistence.qdrant.qdrant_client import QdrantClient
from infrastructure.persistence.qdrant.vector_store import QdrantVectorStore
from infrastructure.storage.minio_storage import MinIOStorage


class Container:

    def __init__(self):
        settings = get_settings()

        # Infrastructure clients
        self.mongodb_client = MongoDBClient()
        self.qdrant_client = QdrantClient()

        # Infrastructure services
        self.storage = MinIOStorage()
        self.loader = PDFLoader()

        self.chunker = Chunker(
            chunk_size=settings.FILE_DEFAULT_CHUNK_SIZE,
            chunk_overlap=settings.FILE_CHUNK_OVERLAP,
        )

        self.embedding_service = BGEM3EmbeddingService()
        self.llm = Qwen3LLMService()

        # Persistence
        self.chunk_repository = MongoChunkRepository(
            self.mongodb_client
        )

        self.vector_store = QdrantVectorStore(
            qdrant_client=self.qdrant_client,
            embedding_service=self.embedding_service,
        )

        # Application services
        self.retrieval_service = RetrievalService(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
        )

        self.context_builder_service = ContextBuilderService()
        self.prompt_builder_service = PromptBuilderService()

        self.recommendation_service = RecommendationService(
            retrieval_service=self.retrieval_service,
            context_builder_service=self.context_builder_service,
            prompt_builder_service=self.prompt_builder_service,
            llm=self.llm,
        )

        self.document_ingestion_service = DocumentIngestionService(
            storage=self.storage,
            loader=self.loader,
            chunker=self.chunker,
            chunk_repository=self.chunk_repository,
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
        )

    async def initialize(self) -> None:
        await self.vector_store.initialize()

    async def close(self) -> None:
        await self.qdrant_client.close()
        self.mongodb_client.close()