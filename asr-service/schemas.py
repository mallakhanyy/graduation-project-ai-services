"""
schemas.py
----------
Pydantic schemas for the ASR Service.

Responsibilities:
- Define request and response models
- Standardize API responses (used both for HTTP responses and for the
  result payload published to RabbitMQ, so the backend sees the exact
  same envelope shape either way)
- Provide automatic FastAPI documentation

This file should NOT:
- Load AI models
- Handle business logic
- Process audio files
"""

from typing import Optional

from pydantic import BaseModel


# ==========================================================
# Metadata
# ==========================================================

class Metadata(BaseModel):
    request_id: Optional[str] = None
    processing_time: Optional[float] = None


# ==========================================================
# Base Response
# ==========================================================

class BaseResponse(BaseModel):
    success: bool
    message: str
    metadata: Optional[Metadata] = None


# ==========================================================
# Data Schemas
# ==========================================================

class HealthData(BaseModel):
    status: str


class InfoData(BaseModel):
    service: str
    description: str


class VersionData(BaseModel):
    version: str


class TranscriptData(BaseModel):
    transcript: str
    language: str = "ar"


class TranscribeAcceptedData(BaseModel):
    request_id: str
    status: str = "processing"


# ==========================================================
# Response Schemas
# ==========================================================

class HealthResponse(BaseResponse):
    data: HealthData


class InfoResponse(BaseResponse):
    data: InfoData


class VersionResponse(BaseResponse):
    data: VersionData


class TranscriptResponse(BaseResponse):
    """Shape of the completed-job message published to the results queue,
    and also usable directly as an HTTP response body if a synchronous
    endpoint is ever added."""
    data: TranscriptData


class TranscribeAcceptedResponse(BaseResponse):
    """Returned immediately by POST /transcribe. The mobile app / backend
    does not wait on this call for the actual transcript — it only
    confirms the job was queued."""
    data: TranscribeAcceptedData


class ErrorResponse(BaseResponse):
    data: None = None