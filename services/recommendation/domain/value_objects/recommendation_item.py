from dataclasses import dataclass

from core.enums.category import Category
from core.enums.priority import Priority


@dataclass
class RecommendationItem:
    recommendation: str
    reasoning: str
    priority: Priority
    category: Category
    confidence: float