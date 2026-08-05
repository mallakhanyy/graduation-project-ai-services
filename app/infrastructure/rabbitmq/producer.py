"""RabbitMQ message producer."""

import json
import time
import pika
from typing import Optional

from app.core.config import settings
from app.core.exceptions import RabbitMQConnectionError
from app.core.logger import logger


class RabbitMQProducer:
    """RabbitMQ producer for sending messages."""
    
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
            self._channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
            self._connected = True
            logger.info("RabbitMQ producer connected")
            
        except Exception as e:
            self._connected = False
            raise RabbitMQConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")
    
    def publish(self, message: dict) -> bool:
        if not self._connected:
            self._connect()
        
        if not self._connected:
            return False
        
        try:
            self._channel.basic_publish(
                exchange="",
                routing_key=settings.rabbitmq_queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )
            logger.info(f"Published message: {message.get('comment_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish: {str(e)}")
            self._connected = False
            return False
    
    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected