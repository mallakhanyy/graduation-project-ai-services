from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Category(Enum):
    IRRIGATION = "irrigation"
    DRAINAGE = "drainage"
    WATER_QUALITY = "water_quality"
    MAINTENANCE = "maintenance"
    RAINWATER_HARVESTING = "rainwater_harvesting"
    SOIL = "soil"
    WATER_MANAGEMENT = "water_management"

@dataclass(frozen=True)
class RecommendationItem:
    recommendation : str
    reasoning : str
    priority: Priority
    category: Category