"""RabbitMQ worker for async moderation."""

import signal
from typing import Any

from app.core.logger import logger
from app.infrastructure.model.arabert_model import AraBERTModel  # ← النموذج الحقيقي
from app.infrastructure.rabbitmq.consumer import RabbitMQConsumer
from app.infrastructure.rabbitmq.result_producer import ResultProducer
from app.services.moderation_service import ModerationService
from app.domain.entities import Comment
from app.domain.value_objects import CommentId, CommentText


class ModerationWorker:
    """Worker for processing moderation requests from RabbitMQ."""
    
    def __init__(self) -> None:
        """Initialize worker."""
        self._running = False
        self._consumer: RabbitMQConsumer | None = None
        
        # Initialize services
        logger.info("Initializing model service...")
        self._model = AraBERTModel()  # ← استخدام النموذج الحقيقي
        self._model.load()
        self._moderation_service = ModerationService(self._model)
        
        # Initialize result producer
        self._result_producer = ResultProducer()
        
        logger.info("Worker initialized successfully")
    
    def _process_message(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a moderation message and send result to results queue.
        """
        try:
            # Create comment
            comment = Comment(
                id=CommentId(data.get("comment_id")) if data.get("comment_id") else None,
                text=CommentText(data["text"]),
            )
            
            # Run moderation
            result = self._moderation_service.moderate(comment)
            
            logger.info(
                f"Moderation completed for {comment.id}: "
                f"{result.label.value} ({result.confidence.value:.2%})"
            )
            
            # Prepare result message
            result_message = {
                "comment_id": comment.id,
                "text": comment.text,
                "label": result.label.value,
                "confidence": result.confidence.value,
                "is_flagged": result.is_flagged,
                "processing_time_ms": result.processing_time_ms,
                "timestamp": result.timestamp.isoformat(),
            }
            
            # Send result to results queue
            success = self._result_producer.publish(result_message)
            
            if success:
                logger.info(f"Result sent to results queue for {comment.id}")
            else:
                logger.warning(f"Failed to send result for {comment.id}")
            
            return result_message
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
    
    def start(self) -> None:
        """Start the worker."""
        logger.info("Starting moderation worker...")
        self._running = True
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._consumer = RabbitMQConsumer(self._process_message)
        self._consumer.start_consuming()
    
    def _signal_handler(self, signum: int, frame: Any) -> None:
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def stop(self) -> None:
        logger.info("Stopping moderation worker...")
        self._running = False
        
        if self._consumer:
            self._consumer.stop_consuming()
        
        if self._result_producer:
            self._result_producer.close()
        
        logger.info("Moderation worker stopped")


if __name__ == "__main__":
    worker = ModerationWorker()
    worker.start()