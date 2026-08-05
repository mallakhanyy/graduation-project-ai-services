"""RabbitMQ message consumer."""

import json
import pika
from typing import Callable

from app.core.config import settings
from app.core.logger import logger


class RabbitMQConsumer:
    """RabbitMQ consumer for processing messages."""
    
    def __init__(self, callback: Callable[[dict], dict]) -> None:
        self._callback = callback
        self._connection = None
        self._channel = None
        self._connected = False
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
            self._channel.basic_qos(prefetch_count=1)
            self._connected = True
            logger.info("RabbitMQ consumer connected")
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
    
    def start_consuming(self) -> None:
        if not self._connected:
            self._connect()
        
        if not self._connected:
            logger.error("Cannot start consuming")
            return
        
        self._channel.basic_consume(
            queue=settings.rabbitmq_queue,
            on_message_callback=self._process_message,
            auto_ack=False,
        )
        logger.info("Started consuming messages")
        self._channel.start_consuming()
    
    def _process_message(self, channel, method, properties, body):
        try:
            data = json.loads(body)
            result = self._callback(data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Message processed: {data.get('comment_id')}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def stop_consuming(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.stop_consuming()
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connected = False