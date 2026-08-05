"""Pydantic response schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ModerationResponse(BaseModel):
    """Moderation response without all_scores."""
    
    comment_id: Optional[str] = None
    text: str
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_flagged: bool
    processing_time_ms: float
    timestamp: datetime


class AsyncModerationResponse(BaseModel):
    """Async moderation response."""
    
    comment_id: Optional[str] = None
    status: str
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    model_loaded: bool
    rabbitmq_connected: bool
    uptime_seconds: float