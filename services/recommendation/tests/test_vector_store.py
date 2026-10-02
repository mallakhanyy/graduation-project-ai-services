import asyncio

from core.value_objects.document_chunk import DocumentChunk

from infrastructure.embeddings.bge_m3_embedding import (
    BGEM3EmbeddingService,
)
from infrastructure.persistence.qdrant.qdrant_client import (
    QdrantClient,
)
from infrastructure.persistence.qdrant.vector_store import (
    QdrantVectorStore,
)


async def main():

    # 1. Create embedding service
    embedding_service = BGEM3EmbeddingService()

    print(
        f"Embedding dimension: "
        f"{embedding_service.dimension}"
    )

    # 2. Create Qdrant client
    qdrant_client = QdrantClient()

    # 3. Create vector store
    vector_store = QdrantVectorStore(
        qdrant_client=qdrant_client,
        embedding_service=embedding_service,
    )

    # 4. Create test chunks
    chunks = [
        DocumentChunk(
            chunk_id="qdrant-test-001",
            text="Irrigation systems need regular maintenance.",
            metadata={
                "document_id": "qdrant-test-document",
                "file_name": "test.pdf",
                "page_number": 1,
            },
            chunk_order=0,
        ),
        DocumentChunk(
            chunk_id="qdrant-test-002",
            text="Rainwater harvesting can help reduce water waste.",
            metadata={
                "document_id": "qdrant-test-document",
                "file_name": "test.pdf",
                "page_number": 2,
            },
            chunk_order=1,
        ),
        DocumentChunk(
            chunk_id="qdrant-test-003",
            text="Drainage problems can cause water accumulation.",
            metadata={
                "document_id": "qdrant-test-document",
                "file_name": "test.pdf",
                "page_number": 3,
            },
            chunk_order=2,
        ),
    ]

    # 5. Generate embeddings
    texts = [chunk.text for chunk in chunks]

    embeddings = await embedding_service.embed_many(texts)

    print(f"Embeddings created: {len(embeddings)}")

    # 6. Save vectors to Qdrant
    await vector_store.add(
        chunks=chunks,
        embeddings=embeddings,
    )

    print("Vectors saved successfully!")

    # 7. Create query embedding
    query = "How can I maintain an irrigation system?"

    query_embedding = await embedding_service.embed(query)

    # 8. Search Qdrant
    results = await vector_store.search(
        embedding=query_embedding,
        top_k=3,
    )

    # 9. Display results
    print("\nSearch results:")

    for result in results:
        print(
            f"\nScore: {result.score}"
            f"\nChunk ID: {result.chunk_id}"
            f"\nText: {result.text}"
        )

    qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(main())