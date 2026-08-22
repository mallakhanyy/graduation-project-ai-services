import asyncio
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

        # 1. Download original PDF from storage (Sync I/O)
        file_bytes = await asyncio.to_thread(
            self.storage.download, object_key
        )

        print(
            f"File downloaded, size: {len(file_bytes)} bytes"
        )

        # 2. Load PDF pages (CPU-bound / Sync)
        pages = await asyncio.to_thread(
            self.loader.load,
            file_bytes,
            object_key,
        )
        print(f"Pages loaded: {len(pages)}")

        # 3. Split pages into chunks (CPU-bound / Sync)
        chunks = await asyncio.to_thread(
            self.chunker.chunk,
            pages=pages,
            document_id=object_key,
        )

        print(f"Chunks created: {len(chunks)}")

        if not chunks:
            print("Warning: No chunks to save.")
            return

        # 4. Save chunks in MongoDB (Async I/O)
        await self.chunk_repository.save_many(chunks)

        print("Chunks saved to DB successfully!")

        # 5. Create embeddings (Heavy CPU/GPU-bound)
        texts = [chunk.text for chunk in chunks]

        embeddings = await asyncio.to_thread(
            self.embedding_service.embed_many, texts
        )

        print(f"Embeddings created: {len(embeddings)}")

        # 6. Save vectors in Qdrant (Async I/O)
        await self.vector_store.add(
            chunks=chunks,
            embeddings=embeddings,
        )

        print("Vectors saved to Qdrant successfully!")

        print("Document ingestion completed successfully.")

    async def ingest_all(self) -> None:

        object_keys = await asyncio.to_thread(
            self.storage.list_objects
        )

        pdf_objects = [
            object_key
            for object_key in object_keys
            if object_key.lower().endswith(".pdf")
        ]

        print(
            f"\nFound {len(pdf_objects)} PDF documents in MinIO."
        )

        if not pdf_objects:
            print("No PDF documents found.")
            return

        for index, object_key in enumerate(
            pdf_objects,
            start=1,
        ):

            print(
                f"\n{'=' * 60}"
            )

            print(
                f"[{index}/{len(pdf_objects)}] "
                f"Ingesting: {object_key}"
            )

            print(
                f"{'=' * 60}"
            )

            try:

                await self.ingest(object_key)

                print(
                    f"Successfully ingested: {object_key}"
                )

            except Exception as e:

                print(
                    f"Failed to ingest: {object_key}"
                )

                print(
                    f"Error: {e}"
                )