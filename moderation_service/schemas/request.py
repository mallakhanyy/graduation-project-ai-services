"""Pydantic request schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ModerationRequest(BaseModel):
    """Comment moderation request."""
    
    comment_id: Optional[str] = Field(None, description="Unique comment identifier")
    text: str = Field(..., min_length=1, max_length=5000, description="Comment text")
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean comment text."""
        if not v or not v.strip():
            raise ValueError("Comment text cannot be empty")
        return v.strip()