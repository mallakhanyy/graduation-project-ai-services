"""RabbitMQ consumer for receiving results."""

import json
import pika
from typing import Callable
from moderation_service.core.config import settings
from moderation_service.core.logger import logger


class ResultConsumer:
    """Consumer for receiving moderation results."""
    
    def __init__(self, callback: Callable[[dict], None]) -> None:
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
            self._channel.queue_declare(queue="results_queue", durable=True)
            self._channel.basic_qos(prefetch_count=1)
            self._connected = True
            logger.info("Result consumer connected")
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect result consumer: {str(e)}")
    
    def start_consuming(self) -> None:
        if not self._connected:
            self._connect()
        
        if not self._connected:
            logger.error("Cannot start consuming results")
            return
        
        self._channel.basic_consume(
            queue="results_queue",
            on_message_callback=self._process_message,
            auto_ack=False,
        )
        logger.info("Started consuming results")
        self._channel.start_consuming()
    
    def _process_message(self, channel, method, properties, body):
        try:
            data = json.loads(body)
            self._callback(data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Result received: {data.get('comment_id')}")
        except Exception as e:
            logger.error(f"Error processing result: {str(e)}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def stop_consuming(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.stop_consuming()
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connected = False