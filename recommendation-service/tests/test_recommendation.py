import asyncio

from application.services.recommendation_service import RecommendationService
from application.services.retrieval_service import RetrievalService
from application.services.context_builder_service import ContextBuilderService
from application.services.prompt_builder_service import PromptBuilderService

from infrastructure.llm.qwen3_llm_service import Qwen3LLMService
from infrastructure.embeddings.bge_m3_embedding import BGEM3EmbeddingService
from infrastructure.persistence.qdrant.qdrant_client import QdrantClient
from infrastructure.persistence.qdrant.vector_store import QdrantVectorStore


async def main():

    # 1. Embedding service
    embedding_service = BGEM3EmbeddingService()

    # 2. Qdrant client
    qdrant_client = QdrantClient()

    # 3. Vector store
    vector_store = QdrantVectorStore(
        qdrant_client=qdrant_client,
        embedding_service=embedding_service,
    )

    # 4. Retrieval service
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # 5. Context builder
    context_builder_service = ContextBuilderService()

    # 6. Prompt builder
    prompt_builder_service = PromptBuilderService()

    # 7. Real local LLM
    llm = Qwen3LLMService()

    # 8. Recommendation service
    recommendation_service = RecommendationService(
        retrieval_service=retrieval_service,
        context_builder_service=context_builder_service,
        prompt_builder_service=prompt_builder_service,
        llm=llm,
    )

    # 9. Test query
    query = "عندي مشكلة في تراكم المياه في الأرض"

    # 10. Run full pipeline
    response = await recommendation_service.recommend(
        request_id="test-123",
        query=query,
        top_k=3,
    )

    # 11. Print result
    print("\n===== FINAL RESPONSE =====")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())