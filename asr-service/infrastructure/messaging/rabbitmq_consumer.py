import aio_pika
import asyncio
from shared.config import settings
from shared.logger import logger
from application.services.transcription_service import TranscriptionService
from shared.file_storage import save_audio, delete_audio
from infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from shared.audio_validator import validate_audio

class RabbitMQConsumer:
    
    def __init__(self, 
                 transcription_service: TranscriptionService, 
                 publisher: RabbitMQPublisher, 
                 queue: aio_pika.abc.AbstractQueue
                ):
        
        self.transcription_service = transcription_service
        self.publisher = publisher
        self.queue = queue

    async def start(self):

        logger.info("Starting RabbitMQ consumer...")

        await self.queue.consume(
            self.process_message
        )

        await asyncio.Future()

    async def process_message(self, message: aio_pika.IncomingMessage):

        audio_path = None

        async with message.process():

            if message.correlation_id is None:
                logger.error("Received message without correlation_id.")
                return
            
            request_id = message.correlation_id
            audio_bytes = message.body
            extension = message.headers.get("extension")

            if extension is None:
                logger.error("Received message without file extension.")
                return
            

            try:
                validate_audio(audio_bytes, extension)
                audio_path = save_audio(audio_bytes, request_id, extension)                
                transcription = await asyncio.to_thread(self.transcription_service.transcribe,request_id,audio_path,)
                await self.publisher.publish(transcription)
            except Exception as e:
                logger.exception(f"Processing failed for request {request_id}")                
                transcription = self.transcription_service.create_failed_transcription(
                                request_id,
                                str(e)
                )
                await self.publisher.publish(transcription)
            finally:
                if audio_path is not None:
                    delete_audio(audio_path)
