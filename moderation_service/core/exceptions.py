"""Custom exceptions for the moderation service."""

from typing import Optional, Any


class ModerationError(Exception):
    """Base exception for moderation service."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ModelLoadError(ModerationError):
    """Raised when model fails to load."""
    pass


class ModelPredictionError(ModerationError):
    """Raised when model prediction fails."""
    pass


class RabbitMQConnectionError(ModerationError):
    """Raised when RabbitMQ connection fails."""
    pass


class InvalidTextError(ModerationError):
    """Raised when text is invalid."""
    pass