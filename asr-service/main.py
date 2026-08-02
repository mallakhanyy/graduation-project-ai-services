import asyncio
import aio_pika
from shared.config import settings
from shared.logger import logger
from infrastructure.models.qwen_asr import QwenASR
from infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from infrastructure.storage.http_audio_downloader import HttpAudioDownloader
from application.services.transcription_service import TranscriptionService
from api import dependencies
import threading
import uvicorn
from api.app import app

def start_api():
    uvicorn.run(
        app,
        host=settings.api.host,
        port=settings.api.port,
    )

def create_transcription_service() -> TranscriptionService:
    asr_model = QwenASR()
    return TranscriptionService(asr_model)

async def main():

    connection = None

    try:

        transcription_service = create_transcription_service()

        dependencies.transcription_service = transcription_service

        api_thread = threading.Thread(
            target=start_api,
            daemon=True,
        )

        api_thread.start()

        audio_downloader = HttpAudioDownloader()

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

        channel: aio_pika.abc.AbstractChannel = (
            await connection.channel()
        )

        await channel.set_qos(
            prefetch_count=settings.rabbitmq.prefetch_count
        )

        requests_queue: aio_pika.abc.AbstractQueue = (
            await channel.declare_queue(
                settings.rabbitmq.requests_queue,
                durable=True,
                auto_delete=False,
            )
        )

        await channel.declare_queue(
            settings.rabbitmq.results_queue,
            durable=True,
            auto_delete=False,
        )

        logger.info(
            "RabbitMQ connected successfully."
        )

        publisher = RabbitMQPublisher(
            channel
        )

        consumer = RabbitMQConsumer(
            transcription_service=transcription_service,
            publisher=publisher,
            queue=requests_queue,
            audio_downloader=audio_downloader,
        )

        await consumer.start()

    finally:

        if connection is not None:

            logger.info(
                "Closing RabbitMQ connection..."
            )

            await connection.close()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info(
            "ASR Service stopped."
        )