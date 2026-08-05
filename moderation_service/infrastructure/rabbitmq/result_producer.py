"""RabbitMQ producer for sending results."""

import json
import pika
from typing import Optional
from moderation_service.core.config import settings
from moderation_service.core.exceptions import RabbitMQConnectionError
from moderation_service.core.logger import logger



class ResultProducer:
    """Producer for sending moderation results."""
    
    def __init__(self) -> None:
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.Channel] = None
        self._connected: bool = False
        self._connect()
    
    def _connect(self) -> None:
        try:
            credentials = pika.PlainCredentials(
                settings.rabbitmq_user,
                settings.rabbitmq_password,
            )
            parameters = pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials,
                heartbeat=settings.rabbitmq_heartbeat,
                blocked_connection_timeout=settings.rabbitmq_timeout,
            )
            
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue="results_queue", durable=True)
            self._connected = True
            logger.info("Result producer connected")
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect result producer: {str(e)}")
    
    def publish(self, result: dict) -> bool:
        if not self._connected:
            self._connect()
        
        if not self._connected:
            return False
        
        try:
            self._channel.basic_publish(
                exchange="",
                routing_key="results_queue",
                body=json.dumps(result),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )
            logger.info(f"Published result: {result.get('comment_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish result: {str(e)}")
            return False
    
    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected