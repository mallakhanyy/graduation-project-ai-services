"""
config.py
----------
Central configuration for the ASR Service.

Responsibilities:
- Store application configuration
- Organize settings into logical sections
- Provide one shared settings object
- Read overrides from environment variables (per the platform spec, nothing
  is hardcoded in business logic — only default values live here)

This file should NOT:
- Load AI models
- Configure logging
- Handle API routes
- Process requests
"""

import os
from dataclasses import dataclass, field


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes")


# ==========================================================
# Service Configuration
# ==========================================================

@dataclass(frozen=True)
class ServiceConfig:
    name: str = field(default_factory=lambda: _env("SERVICE_NAME", "ASR Service"))
    description: str = field(default_factory=lambda: _env(
        "SERVICE_DESCRIPTION", "Automatic Speech Recognition API"
    ))
    version: str = field(default_factory=lambda: _env("SERVICE_VERSION", "1.0.0"))
    environment: str = field(default_factory=lambda: _env("SERVICE_ENVIRONMENT", "development"))


# ==========================================================
# Server Configuration
# ==========================================================

@dataclass(frozen=True)
class ServerConfig:
    host: str = field(default_factory=lambda: _env("SERVER_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _env_int("SERVER_PORT", 8000))


# ==========================================================
# Model Configuration
# ==========================================================

@dataclass(frozen=True)
class ModelConfig:
    name: str = field(default_factory=lambda: _env("MODEL_NAME", "mohammedaly22/QwenCleo-ASR"))
    device: str = field(default_factory=lambda: _env("MODEL_DEVICE", "auto"))
    trust_remote_code: bool = field(default_factory=lambda: _env_bool("MODEL_TRUST_REMOTE_CODE", True))


# ==========================================================
# Audio Configuration
# ==========================================================

@dataclass(frozen=True)
class AudioConfig:
    supported_formats: list[str] = field(default_factory=lambda: [
        ".wav",
        ".mp3",
        ".flac",
        ".m4a",
    ])

    max_file_size_mb: int = field(default_factory=lambda: _env_int("AUDIO_MAX_FILE_SIZE_MB", 25))
    max_duration_sec: int = field(default_factory=lambda: _env_int("AUDIO_MAX_DURATION_SEC", 60))
    sample_rate: int = field(default_factory=lambda: _env_int("AUDIO_SAMPLE_RATE", 16000))


# ==========================================================
# Storage Configuration
# ==========================================================

@dataclass(frozen=True)
class StorageConfig:
    # Local scratch space for uploaded audio while it waits to be picked up
    # by the background worker. Files are deleted right after processing —
    # the service stays stateless between requests.
    upload_dir: str = field(default_factory=lambda: _env("ASR_UPLOAD_DIR", "/tmp/asr_uploads"))


# ==========================================================
# Logging Configuration
# ==========================================================

@dataclass(frozen=True)
class LoggingConfig:
    level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))


# ==========================================================
# RabbitMQ Configuration
# ==========================================================

@dataclass(frozen=True)
class RabbitMQConfig:
    host: str = field(default_factory=lambda: _env("RABBITMQ_HOST", "localhost"))
    port: int = field(default_factory=lambda: _env_int("RABBITMQ_PORT", 5672))
    user: str = field(default_factory=lambda: _env("RABBITMQ_USER", "guest"))
    password: str = field(default_factory=lambda: _env("RABBITMQ_PASSWORD", "guest"))
    vhost: str = field(default_factory=lambda: _env("RABBITMQ_VHOST", "/"))

    # Jobs waiting to be transcribed (this service is the consumer).
    requests_queue: str = field(default_factory=lambda: _env(
        "RABBITMQ_REQUESTS_QUEUE", "asr.transcription.requests"
    ))
    # Completed transcripts / failures (the .NET backend is the consumer).
    results_queue: str = field(default_factory=lambda: _env(
        "RABBITMQ_RESULTS_QUEUE", "asr.transcription.results"
    ))

    # How many jobs the worker pulls at once. Kept at 1 by default since a
    # single model instance processes one audio file at a time anyway.
    prefetch_count: int = field(default_factory=lambda: _env_int("RABBITMQ_PREFETCH_COUNT", 1))


# ==========================================================
# Main Settings
# ==========================================================

@dataclass(frozen=True)
class Settings:
    service: ServiceConfig = field(default_factory=ServiceConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    rabbitmq: RabbitMQConfig = field(default_factory=RabbitMQConfig)


# ==========================================================
# Global Settings Instance
# ==========================================================

settings = Settings()