from pydantic import BaseModel, Field

from core.enums.category import Category
from core.enums.priority import Priority


class RecommendationItemResponse(BaseModel):
    recommendation: str
    reasoning: str
    priority: Priority
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)


class RecommendationResponse(BaseModel):
    request_id: str
    problem: str
    recommendations: list[RecommendationItemResponse]