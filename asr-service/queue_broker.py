"""
queue_broker.py
----------------
RabbitMQ messaging layer for the ASR Service.

Responsibilities:
- Connect to RabbitMQ
- Publish transcription jobs so the HTTP layer never has to wait on the
  model (POST /transcribe returns as soon as a job is queued)
- Publish completed results for the .NET backend to consume — this is
  the "notification" hop: once a job finishes, the backend picks the
  message up from `results_queue` and can push a notification to the
  mobile app
- Run the internal job consumer loop that feeds the model

This file should NOT:
- Contain model inference logic
- Contain HTTP route logic
"""

import json
from typing import Awaitable, Callable, Optional

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from config import settings
from logger import logger


class RabbitMQBroker:
    """Thin wrapper around aio-pika. One connection, one channel, two
    durable queues: one this service consumes (requests_queue) and one
    the backend consumes (results_queue)."""

    def __init__(self):
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractChannel] = None

    async def connect(self) -> None:
        url = (
            f"amqp://{settings.rabbitmq.user}:{settings.rabbitmq.password}"
            f"@{settings.rabbitmq.host}:{settings.rabbitmq.port}{settings.rabbitmq.vhost}"
        )

        logger.info(f"Connecting to RabbitMQ at {settings.rabbitmq.host}:{settings.rabbitmq.port}...")

        self._connection = await aio_pika.connect_robust(url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=settings.rabbitmq.prefetch_count)

        # Durable: survive a RabbitMQ restart without losing queued jobs.
        await self._channel.declare_queue(settings.rabbitmq.requests_queue, durable=True)
        await self._channel.declare_queue(settings.rabbitmq.results_queue, durable=True)

        logger.info("Connected to RabbitMQ.")

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed.")

    async def publish_request(self, payload: dict) -> None:
        await self._publish(settings.rabbitmq.requests_queue, payload)

    async def publish_result(self, payload: dict) -> None:
        await self._publish(settings.rabbitmq.results_queue, payload)

    async def _publish(self, queue_name: str, payload: dict) -> None:
        if self._channel is None:
            raise RuntimeError("RabbitMQ channel is not connected.")

        message = aio_pika.Message(
            body=json.dumps(payload, default=str).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await self._channel.default_exchange.publish(message, routing_key=queue_name)

    async def consume_requests(self, handler: Callable[[dict], Awaitable[None]]) -> None:
        """Runs forever, pulling one job at a time off requests_queue and
        awaiting `handler(payload)`. The message is only acked after the
        handler completes, so a crash mid-transcription puts the job back
        on the queue instead of losing it."""

        if self._channel is None:
            raise RuntimeError("RabbitMQ channel is not connected.")

        queue = await self._channel.declare_queue(settings.rabbitmq.requests_queue, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode())
                        await handler(payload)
                    except Exception as e:
                        logger.error(f"Failed to process queued job: {e}")


# ==========================================================
# Global Broker Instance
# ==========================================================

broker = RabbitMQBroker()