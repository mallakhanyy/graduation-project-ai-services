from dataclasses import dataclass, field
from core.value_objects.recommendation_item import RecommendationItem
from core.entities.retrieved_chunk import RetrievedChunk

@dataclass
class Recommendation:
    request_id : str
    problem : str
    recommendations : list[RecommendationItem] = field(default_factory=list)
    retrieved_chunks : list[RetrievedChunk] = field(default_factory=list)
    