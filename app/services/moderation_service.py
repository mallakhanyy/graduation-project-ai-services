"""Core moderation service."""

import time

from app.core.exceptions import InvalidTextError
from app.core.logger import logger
from app.core.config import settings
from app.domain.entities import Comment, ModerationResult
from app.domain.value_objects import Confidence, ModerationLabel
from app.services.interfaces.model_service_interface import ModelService


class ModerationService:
    """Service for moderating comments."""
    
    def __init__(self, model_service: ModelService) -> None:
        self._model_service = model_service
        logger.info("ModerationService initialized")
    
    def moderate(self, comment: Comment) -> ModerationResult:
        """Moderate a single comment."""
        if not comment.text or not comment.text.strip():
            raise InvalidTextError("Comment text cannot be empty")
        
        start_time = time.time()
        
        try:
            label, confidence, _ = self._model_service.predict(comment.text)
            
            processing_time = (time.time() - start_time) * 1000
            confidence_obj = Confidence(confidence)
            
            return ModerationResult(
                comment_id=comment.id,
                text=comment.text,
                label=ModerationLabel(label),
                confidence=confidence_obj,
                is_flagged=confidence_obj.is_flagged(settings.confidence_threshold),
                processing_time_ms=processing_time,
            )
        except Exception as e:
            logger.error(f"Moderation failed: {str(e)}")
            raise
    
    def is_model_loaded(self) -> bool:
        return self._model_service.is_loaded()