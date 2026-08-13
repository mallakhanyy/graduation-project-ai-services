from dataclasses import dataclass

from core.value_objects.recommendation_item import RecommendationItem


@dataclass
class Recommendation:
    request_id: str
    problem: str
    recommendations: list[RecommendationItem]