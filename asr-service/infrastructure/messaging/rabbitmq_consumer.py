import asyncio
import json

import aio_pika

from shared.config import settings
from shared.logger import logger
from shared.audio_validator import validate_extension
from shared.file_storage import get_audio_path, delete_audio

from core.value_objects.transcription_request import TranscriptionRequest
from application.services.transcription_service import TranscriptionService
from infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from core.interfaces.audio_downloader import AudioDownloader


class RabbitMQConsumer:

    def __init__(
        self,
        transcription_service: TranscriptionService,
        publisher: RabbitMQPublisher,
        queue: aio_pika.abc.AbstractQueue,
        audio_downloader: AudioDownloader,
    ):
        self.transcription_service = transcription_service
        self.publisher = publisher
        self.queue = queue
        self.audio_downloader = audio_downloader

    async def start(self):

        logger.info("Starting RabbitMQ consumer...")

        await self.queue.consume(
            self.process_message
        )

        await asyncio.Future()

    async def process_message(
        self,
        message: aio_pika.IncomingMessage,
    ):

        audio_path = None

        async with message.process():

            if message.correlation_id is None:
                logger.error(
                    "Received message without correlation_id."
                )
                return

            request_id = message.correlation_id

            try:
                payload = json.loads(
                    message.body.decode("utf-8")
                )

                request = TranscriptionRequest(
                    request_id=request_id,
                    audio_url=payload["audio_url"],
                    extension=payload["extension"],
                )

                extension = validate_extension(
                    request.extension
                )

                audio_path = get_audio_path(
                    request.request_id,
                    extension,
                )

                max_size_bytes = (
                    settings.audio.max_upload_size_mb
                    * 1024
                    * 1024
                )

                await self.audio_downloader.download(
                    audio_url=request.audio_url,
                    destination_path=audio_path,
                    max_size_bytes=max_size_bytes,
                )

                transcription = await asyncio.to_thread(
                    self.transcription_service.transcribe,
                    request.request_id,
                    audio_path,
                )

                await self.publisher.publish(
                    transcription
                )

            except Exception as e:

                logger.exception(
                    f"Processing failed for request {request_id}"
                )

                transcription = (
                    self.transcription_service
                    .create_failed_transcription(
                        request_id,
                        str(e),
                    )
                )

                await self.publisher.publish(
                    transcription
                )

            finally:

                if audio_path is not None:
                    delete_audio(audio_path)