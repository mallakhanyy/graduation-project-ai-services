import asyncio
import aio_pika

from shared.config import settings
from shared.logger import logger

from infrastructure.models.qwen_asr import QwenASR
from application.services.transcription_service import TranscriptionService
from infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher


async def main():

    connection = None

    try:
        asr_model = QwenASR()

        transcription_service = TranscriptionService(asr_model)

        logger.info("Connecting to RabbitMQ...")

        connection: aio_pika.abc.AbstractRobustConnection = (
            await aio_pika.connect_robust(
                host=settings.rabbitmq.host,
                port=settings.rabbitmq.port,
                login=settings.rabbitmq.user,
                password=settings.rabbitmq.password,
                virtualhost=settings.rabbitmq.vhost,
            )
        )

        channel: aio_pika.abc.AbstractChannel = await connection.channel()

        await channel.set_qos(
            prefetch_count=settings.rabbitmq.prefetch_count
        )

        # Queue that receives requests from .NET
        queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
            settings.rabbitmq.requests_queue,
            durable=True,
            auto_delete=False,
        )

        # Queue that sends results back to .NET
        await channel.declare_queue(
            settings.rabbitmq.results_queue,
            durable=True,
            auto_delete=False,
        )

        logger.info("RabbitMQ connected successfully.")

        publisher = RabbitMQPublisher(channel)

        consumer = RabbitMQConsumer(
            transcription_service,
            publisher,
            queue,
        )

        await consumer.start()

    finally:
        if connection is not None:
            logger.info("Closing RabbitMQ connection...")
            await connection.close()


if __name__ == "__main__":
    asyncio.run(main())