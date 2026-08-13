import asyncio

from application.services.retrieval_service import RetrievalService
from infrastructure.embeddings.bge_m3_embedding import BGEM3EmbeddingService
from infrastructure.persistence.qdrant.qdrant_client import QdrantClient
from infrastructure.persistence.qdrant.vector_store import QdrantVectorStore


async def main():

    # 1. Create embedding service
    embedding_service = BGEM3EmbeddingService()

    # 2. Create Qdrant client
    qdrant_client = QdrantClient()

    # 3. Create vector store
    vector_store = QdrantVectorStore(
        qdrant_client=qdrant_client,
        embedding_service=embedding_service,
    )

    # 4. Create retrieval service
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # 5. Test query
    query = "عندي مشكلة في تراكم المياه في الأرض"

    results = await retrieval_service.retrieve(
        query=query,
        top_k=5,
    )

    # 6. Print results
    print(f"\nQuery: {query}")
    print(f"Results: {len(results)}\n")

    for result in results:
        print(f"Score: {result.score}")
        print(f"Chunk ID: {result.chunk_id}")
        print(f"Text: {result.text}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())