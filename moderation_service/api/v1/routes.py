"""API routes for moderation endpoints."""

import time
from fastapi import APIRouter, HTTPException

from moderation_service.api.v1.dependencies import (
    ModerationServiceDep,
    RabbitMQProducerDep,
)
from moderation_service.core.config import settings
from moderation_service.core.logger import logger
from moderation_service.domain.entities import Comment
from moderation_service.domain.value_objects import CommentId, CommentText
from moderation_service.schemas.request import ModerationRequest
from moderation_service.schemas.response import (
    ModerationResponse,
    AsyncModerationResponse,
    HealthResponse,
)

router = APIRouter()
_start_time = time.time()


@router.post("/moderate", response_model=ModerationResponse)
async def moderate_comment(
    request: ModerationRequest,
    moderation_service: ModerationServiceDep,
) -> ModerationResponse:
    """Moderate a comment synchronously."""
    try:
        comment = Comment(
            id=CommentId(request.comment_id) if request.comment_id else None,
            text=CommentText(request.text),
        )
        
        result = moderation_service.moderate(comment)
        
        return ModerationResponse(
            comment_id=result.comment_id,
            text=result.text,
            label=result.label.value,
            confidence=result.confidence.value,
            is_flagged=result.is_flagged,
            processing_time_ms=result.processing_time_ms,
            timestamp=result.timestamp,
        )
    except Exception as e:
        logger.error(f"Error moderating comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moderate/async", response_model=AsyncModerationResponse)
async def moderate_comment_async(
    request: ModerationRequest,
    rabbitmq_producer: RabbitMQProducerDep,
    moderation_service: ModerationServiceDep,
) -> AsyncModerationResponse:
    """Submit comment for async moderation."""
    try:
        if rabbitmq_producer is None or not rabbitmq_producer.is_connected:
            logger.warning("RabbitMQ unavailable, processing synchronously")
            comment = Comment(
                id=CommentId(request.comment_id) if request.comment_id else None,
                text=CommentText(request.text),
            )
            result = moderation_service.moderate(comment)
            return AsyncModerationResponse(
                comment_id=result.comment_id,
                status="processed",
                message="Comment processed synchronously (RabbitMQ unavailable)",
            )
        
        message = {"comment_id": request.comment_id, "text": request.text}
        success = rabbitmq_producer.publish(message)
        
        if success:
            return AsyncModerationResponse(
                comment_id=request.comment_id,
                status="accepted",
                message="Comment submitted for async moderation",
            )
        else:
            comment = Comment(
                id=CommentId(request.comment_id) if request.comment_id else None,
                text=CommentText(request.text),
            )
            result = moderation_service.moderate(comment)
            return AsyncModerationResponse(
                comment_id=result.comment_id,
                status="processed",
                message="Comment processed synchronously (publish failed)",
            )
    except Exception as e:
        logger.error(f"Error submitting async moderation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check(
    moderation_service: ModerationServiceDep,
    rabbitmq_producer: RabbitMQProducerDep,
) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if moderation_service.is_model_loaded() else "degraded",
        version=settings.app_version,
        model_loaded=moderation_service.is_model_loaded(),
        rabbitmq_connected=rabbitmq_producer is not None and rabbitmq_producer.is_connected,
        uptime_seconds=time.time() - _start_time,
    )


@router.get("/ready")
async def readiness(
    moderation_service: ModerationServiceDep,
) -> dict:
    """Kubernetes readiness probe."""
    if moderation_service.is_model_loaded():
        return {"status": "ready"}
    return {"status": "not_ready"}, 503


@router.get("/live")
async def liveness() -> dict:
    """Kubernetes liveness probe."""
    return {"status": "alive"}