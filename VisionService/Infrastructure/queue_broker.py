"""
RabbitMQ connection and queue management for Vision Service.

Architecture:
    Backend → RabbitMQ (vision.analysis.request) → Worker → RabbitMQ (vision.analysis.result) → Backend

The Worker ONLY:
    - Consumes requests from REQUESTS_QUEUE
    - Publishes results/errors to RESULTS_QUEUE

NOTE: publish_request() has been REMOVED because the Backend now publishes
      requests directly to RabbitMQ.
"""

import pika
import json
import logging
from typing import Dict, Any, Callable
from datetime import datetime

from Infrastructure.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RabbitMQBroker:
    """RabbitMQ connection manager for Vision Service."""

    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()

    # ============================================
    # CONNECT
    # ============================================
    def _connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host='/',
                credentials=credentials,
                heartbeat=600
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # ✅ Declare NEW queues (durable = survive RabbitMQ restart)
            self.channel.queue_declare(
                queue=settings.REQUESTS_QUEUE,  # vision.analysis.request
                durable=True
            )
            self.channel.queue_declare(
                queue=settings.RESULTS_QUEUE,   # vision.analysis.result
                durable=True
            )

            logger.info(
                f"✅ Connected to RabbitMQ at "
                f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT} | "
                f"Requests: {settings.REQUESTS_QUEUE} | "
                f"Results: {settings.RESULTS_QUEUE}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise

    # ============================================
    # PUBLISH RESULT (Success)
    # ============================================
    def publish_result(
        self,
        request_id: str,
        result: Dict[str, Any],
        processing_time: float
    ):
        """
        Publish a successful prediction result to the results queue.

        Args:
            request_id: Unique request ID
            result: Prediction result dictionary
            processing_time: Time taken to process
        """
        try:
            message = {
                "request_id": request_id,
                "success": True,
                "result": result,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RESULTS_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json'
                )
            )
            logger.info(f"📤 Published result for request: {request_id}")
        except Exception as e:
            logger.error(f"❌ Failed to publish result: {e}")
            raise

    # ============================================
    # PUBLISH ERROR
    # ============================================
    def publish_error(
        self,
        request_id: str,
        error_message: str,
        processing_time: float
    ):
        """
        Publish an error result to the results queue.

        Args:
            request_id: Unique request ID
            error_message: Error description
            processing_time: Time taken before failure
        """
        try:
            message = {
                "request_id": request_id,
                "success": False,
                "error": error_message,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RESULTS_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            logger.info(f"📤 Published error for request: {request_id}")
        except Exception as e:
            logger.error(f"❌ Failed to publish error: {e}")
            raise

    # ============================================
    # CONSUME REQUESTS
    # ============================================
    def consume_requests(self, callback: Callable):
        """
        Consume prediction requests from the requests queue.

        Args:
            callback: Function to process requests
        """
        try:
            self.channel.basic_qos(prefetch_count=1)  # process one at a time
            self.channel.basic_consume(
                queue=settings.REQUESTS_QUEUE,
                on_message_callback=callback,
                auto_ack=False
            )
            logger.info(f"👂 Started consuming from: {settings.REQUESTS_QUEUE}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"❌ Failed to consume requests: {e}")
            raise

    # ============================================
    # CLOSE
    # ============================================
    def close(self):
        """Close the connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("🔌 RabbitMQ connection closed")