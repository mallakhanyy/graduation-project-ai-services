from abc import ABC, abstractmethod

from core.schemas.llm_recommendation_response import LLMRecommendationResponse


class LLMService(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
    ) -> LLMRecommendationResponse:
        pass