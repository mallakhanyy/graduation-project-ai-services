from application.services.retrieval_service import RetrievalService
from application.services.context_builder_service import ContextBuilderService
from application.services.prompt_builder_service import PromptBuilderService
from core.interfaces.llm_service import LLMService

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

    async def recommend(
        self,
        query: str,
        top_k: int,
    ) -> str:

        retrieved_chunks = await self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
        )

        context = self.context_builder_service.build(
            retrieved_chunks
        )

        prompt = self.prompt_builder_service.build(
            query=query,
            context=context,
        )

        return await self.llm.generate(prompt)