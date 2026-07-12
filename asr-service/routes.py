"""
routes.py
----------
HTTP routing layer for the ASR Service.

Responsibilities:
- Receive requests
- Validate inputs
- Hand work off to the model layer (indirectly, via the job queue)
- Return standardized responses

This file should NOT:
- Load the model
- Run inference directly
- Contain RabbitMQ connection/consumer setup (that's queue_broker.py + app.py)
"""

import os
import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from config import settings
from logger import logger
from queue_broker import broker
from schemas import (
    HealthData,
    HealthResponse,
    InfoData,
    InfoResponse,
    TranscribeAcceptedData,
    TranscribeAcceptedResponse,
    VersionData,
    VersionResponse,
)

router = APIRouter()


# ==========================================================
# Service Metadata Endpoints
# ==========================================================

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        success=True,
        message="Service is healthy.",
        data=HealthData(status="ok"),
    )


@router.get("/info", response_model=InfoResponse)
async def info():
    return InfoResponse(
        success=True,
        message="Service information.",
        data=InfoData(
            service=settings.service.name,
            description=settings.service.description,
        ),
    )


@router.get("/version", response_model=VersionResponse)
async def version():
    return VersionResponse(
        success=True,
        message="Service version.",
        data=VersionData(version=settings.service.version),
    )


# ==========================================================
# Inference Endpoint
# ==========================================================

@router.post("/transcribe", response_model=TranscribeAcceptedResponse, status_code=202)
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("Arabic"),
):
    """Accepts an audio file, queues it for transcription, and returns
    immediately. It does NOT wait for the model — the caller (the .NET
    backend) is notified of the result later via the RabbitMQ results
    queue, keyed by the same request_id returned here."""

    request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.audio.supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: '{ext or 'unknown'}'. "
                   f"Supported formats: {', '.join(settings.audio.supported_formats)}",
        )

    os.makedirs(settings.storage.upload_dir, exist_ok=True)
    dest_path = os.path.join(settings.storage.upload_dir, f"{request_id}{ext}")
    max_bytes = settings.audio.max_file_size_mb * 1024 * 1024

    size = 0
    try:
        with open(dest_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    out_file.close()
                    os.remove(dest_path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File exceeds the maximum allowed size of {settings.audio.max_file_size_mb} MB.",
                    )
                out_file.write(chunk)
    finally:
        await file.close()

    logger.info(
        f"RequestID={request_id} | Received audio file "
        f"({size / 1024:.1f} KB), queuing for transcription."
    )

    await broker.publish_request({
        "request_id": request_id,
        "audio_path": dest_path,
        "language": language,
        "received_at": time.time(),
    })

    return TranscribeAcceptedResponse(
        success=True,
        message="Request accepted for processing. The result will be delivered asynchronously.",
        data=TranscribeAcceptedData(request_id=request_id, status="processing"),
    )