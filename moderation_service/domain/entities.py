"""Domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.value_objects import (
    CommentId,
    CommentText,
    ModerationLabel,
    Confidence,
)


@dataclass(frozen=True)
class Comment:
    """Comment entity."""
    id: Optional[CommentId]
    text: CommentText
    
    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("Comment text cannot be empty")


@dataclass
class ModerationResult:
    """Result of moderation process."""
    comment_id: Optional[CommentId]
    text: CommentText
    label: ModerationLabel
    confidence: Confidence
    is_flagged: bool
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)