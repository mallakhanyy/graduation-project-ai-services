"""Value objects for domain entities."""

from enum import Enum
from typing import NewType
from dataclasses import dataclass


class ModerationLabel(str, Enum):
    """Classification labels."""
    RELEVANT = "Relevant"
    SPAM = "Spam"
    OFFENSIVE = "Offensive"
    IRRELEVANT = "Irrelevant"
    
    @classmethod
    def from_int(cls, value: int) -> "ModerationLabel":
        """Convert integer to label."""
        mapping = {
            0: cls.RELEVANT,
            1: cls.SPAM,
            2: cls.OFFENSIVE,
            3: cls.IRRELEVANT,
        }
        return mapping[value]


@dataclass(frozen=True)
class Confidence:
    """Confidence score value object."""
    value: float
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
    
    def is_flagged(self, threshold: float) -> bool:
        """Check if confidence is below threshold."""
        return self.value < threshold


CommentId = NewType("CommentId", str)
CommentText = NewType("CommentText", str)