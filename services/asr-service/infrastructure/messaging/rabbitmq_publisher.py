import aio_pika
import json
from core.entities.transcription import Transcription
from shared.config import settings
from shared.logger import logger

class RabbitMQPublisher:

    def __init__(self, channel: aio_pika.abc.AbstractChannel):
        self.channel = channel

    async def publish(self, transcription: Transcription) -> None:

        message = {
            "request_id": transcription.request_id,
            "status": transcription.status.value,
            "text": transcription.text,
            "processing_time": transcription.processing_time,
            "error": transcription.error
        }

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body = json.dumps(message).encode(),
                correlation_id = transcription.request_id,
                content_type = "application/json"
            ),
            routing_key = settings.rabbitmq.results_queue,
        )

        logger.info(
            f"Transcription result published for request: {transcription.request_id}"
        )