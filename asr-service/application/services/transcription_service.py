import time
from core.entities.transcription import Transcription
from core.interfaces.asr_model import ASRModel
from core.value_objects.asr_result import ASRResult
from shared.logger import logger

class TranscriptionService:
    def __init__(self, asr_model: ASRModel):
        self.asr_model = asr_model

    
    def transcribe(self, request_id: str, audio_path: str) -> Transcription:
        transcription = Transcription (
            request_id = request_id
        )
        
        logger.info(
            f"Starting transcription request: {request_id}"
        )

        transcription.start_processing()
        start_time = time.perf_counter()

        try:
            asr_result: ASRResult = self.asr_model.transcribe(audio_path)

        except Exception as e:
            processing_time = time.perf_counter() - start_time

            logger.error(
                f"Transcription failed for request {request_id}: {e}"
            )

            transcription.fail(str(e), processing_time)
            return transcription
        
        processing_time = time.perf_counter() - start_time

        transcription.complete(asr_result.text, processing_time)

        logger.info(
            f"Transcription completed successfully: {request_id}"
        )

        return transcription
    
    def create_failed_transcription(self, request_id: str, error: str) -> Transcription:

        transcription = Transcription(request_id=request_id)
        start_time = time.perf_counter()
        logger.error(f"Validation failed for request {request_id}: {error}")
        transcription.start_processing()
        processing_time = time.perf_counter() - start_time
        transcription.fail(error, processing_time)

        return transcription