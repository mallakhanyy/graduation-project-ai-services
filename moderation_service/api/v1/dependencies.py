"""Dependency injection for API routes."""

from fastapi import Depends
from typing import Annotated

from moderation_service.services.moderation_service import ModerationService
from moderation_service.infrastructure.model.arabert_model import AraBERTModel
from moderation_service.infrastructure.rabbitmq.producer import RabbitMQProducer
from moderation_service.core.logger import logger

# Singleton instances
_model_service = None
_moderation_service = None
_rabbitmq_producer = None


def get_model_service() -> AraBERTModel:
    """Get or create model service instance."""
    global _model_service
    if _model_service is None:
        try:
            _model_service = AraBERTModel()
            _model_service.load()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            _model_service = None
    return _model_service


def get_moderation_service(
    model_service: AraBERTModel = Depends(get_model_service),
) -> ModerationService:
    """Get or create moderation service instance."""
    global _moderation_service
    if _moderation_service is None:
        _moderation_service = ModerationService(model_service)
    return _moderation_service


def get_rabbitmq_producer() -> RabbitMQProducer:
    """Get or create RabbitMQ producer instance."""
    global _rabbitmq_producer
    if _rabbitmq_producer is None:
        try:
            _rabbitmq_producer = RabbitMQProducer()
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            _rabbitmq_producer = None
    return _rabbitmq_producer


# Type hints for dependency injection
ModelServiceDep = Annotated[AraBERTModel, Depends(get_model_service)]
ModerationServiceDep = Annotated[ModerationService, Depends(get_moderation_service)]
RabbitMQProducerDep = Annotated[RabbitMQProducer, Depends(get_rabbitmq_producer)]