from core.interfaces.chunk_repository import ChunkRepository
from core.interfaces.document_loader import DocumentLoader
from core.interfaces.embedding_service import EmbeddingService
from core.interfaces.file_storage import FileStorage
from core.interfaces.vector_store import VectorStore
from core.interfaces.chunker import Chunker


class DocumentIngestionService:

    def __init__(
        self,
        storage: FileStorage,
        loader: DocumentLoader,
        chunker: Chunker,
        chunk_repository: ChunkRepository,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.storage = storage
        self.loader = loader
        self.chunker = chunker
        self.chunk_repository = chunk_repository
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def ingest(self, object_key: str) -> None:

        # 1. Download original PDF from storage
        file_bytes = self.storage.download(object_key)

        print(
            f"File downloaded, size: {len(file_bytes)} bytes"
        )

        # 2. Load PDF pages
        pages = self.loader.load(file_bytes)

        print(f"Pages loaded: {len(pages)}")

        # 3. Split pages into chunks
        chunks = self.chunker.chunk(
            pages=pages,
            document_id=object_key,
        )

        print(f"Chunks created: {len(chunks)}")

        if not chunks:
            print("Warning: No chunks to save.")
            return

        # 4. Save chunks in MongoDB
        await self.chunk_repository.save_many(chunks)

        print("Chunks saved to DB successfully!")

        # 5. Create embeddings
        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedding_service.embed_many(texts)

        print(f"Embeddings created: {len(embeddings)}")

        # 6. Save vectors in Qdrant
        await self.vector_store.add(
            chunks=chunks,
            embeddings=embeddings,
        )

        print("Vectors saved to Qdrant successfully!")

        print("Document ingestion completed successfully.")