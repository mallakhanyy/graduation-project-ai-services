from pydantic import BaseModel

from core.schemas.recommendation_response import RecommendationItemResponse


class LLMRecommendationResponse(BaseModel):
    problem: str
    recommendations: list[RecommendationItemResponse]