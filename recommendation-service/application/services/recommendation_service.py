from application.services.retrieval_service import RetrievalService
from application.services.context_builder_service import ContextBuilderService
from application.services.prompt_builder_service import PromptBuilderService

from core.interfaces.llm_service import LLMService
from core.schemas.recommendation_response import RecommendationResponse

from shared.config import get_settings


class RecommendationService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_builder_service: ContextBuilderService,
        prompt_builder_service: PromptBuilderService,
        llm: LLMService,
    ):
        self.retrieval_service = retrieval_service
        self.context_builder_service = context_builder_service
        self.prompt_builder_service = prompt_builder_service
        self.llm = llm
        self.settings = get_settings()

    async def recommend(
        self,
        request_id: str,
        query: str,
        top_k: int,
    ) -> RecommendationResponse:

        retrieved_chunks = await self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
        )

        print("\n===== RETRIEVED CHUNKS =====")
        print(f"Query: {query}")
        print(f"Retrieved: {len(retrieved_chunks)} chunks\n")

        for index, chunk in enumerate(retrieved_chunks, start=1):
            print(f"--- Chunk {index} ---")
            print(f"Chunk ID: {chunk.chunk_id}")
            print(f"Score: {chunk.score}")
            print(f"Metadata: {chunk.metadata}")
            print(f"Text:\n{chunk.text}")
            print()

        context = self.context_builder_service.build(
            retrieved_chunks
        )

        print("\n===== BUILT CONTEXT =====")
        print(context)
        print("=========================\n")        

        prompt = self.prompt_builder_service.build(
            query=query,
            context=context,
            max_recommendations=self.settings.MAX_RECOMMENDATIONS,
        )

        print("\n===== FINAL PROMPT =====")
        print(prompt)
        print("========================\n")

        llm_result = await self.llm.generate(prompt)

        return RecommendationResponse(
            request_id=request_id,
            problem=llm_result.problem,
            recommendations=llm_result.recommendations,
        )