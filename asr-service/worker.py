"""
worker.py
----------
Background job processor for the ASR Service.

Responsibilities:
- Pull queued transcription jobs and run them through the model
- Turn the result (or failure) into the standard response envelope
- Publish that envelope to the results queue for the .NET backend
- Clean up the temporary audio file once done

This file should NOT:
- Handle HTTP requests
- Talk to RabbitMQ directly (that's queue_broker.py's job)
- Contain model-loading logic (that's model.py's job)
"""

import asyncio
import os
import time

from logger import logger
from model import asr_model
from schemas import ErrorResponse, Metadata, TranscriptData, TranscriptResponse


async def process_transcription_job(payload: dict) -> "TranscriptResponse | ErrorResponse":
    """Runs one transcription job and returns the result envelope.

    The caller (app.py's consumer loop) is responsible for publishing the
    returned envelope to the results queue — this function's only job is
    to turn a queued request into a finished result.
    """

    request_id = payload.get("request_id")
    audio_path = payload.get("audio_path")
    language = payload.get("language", "Arabic")

    logger.info(f"RequestID={request_id} | Starting transcription job.")
    start = time.time()

    # model.transcribe() is a blocking, CPU/GPU-bound call — running it in
    # a worker thread keeps the event loop free to keep accepting new
    # /transcribe uploads while a job is in flight.
    loop = asyncio.get_running_loop()

    try:
        transcript = await loop.run_in_executor(
            None, asr_model.transcribe, audio_path, language
        )

        elapsed = round(time.time() - start, 2)

        result = TranscriptResponse(
            success=True,
            message="Transcription completed successfully.",
            data=TranscriptData(transcript=transcript, language=language),
            metadata=Metadata(request_id=request_id, processing_time=elapsed),
        )

        logger.info(f"RequestID={request_id} | Transcription completed in {elapsed}s.")
        return result

    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"RequestID={request_id} | Transcription failed: {e}")

        return ErrorResponse(
            success=False,
            message="Transcription failed.",
            metadata=Metadata(request_id=request_id, processing_time=elapsed),
        )

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)