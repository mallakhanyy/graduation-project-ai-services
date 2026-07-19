import os
from dataclasses import dataclass, field


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(
        name,
        str(default)
    ).lower() in ("true", "1", "yes")


def _env_list(name: str, default: str) -> list[str]:
    return [
        item.strip().lower()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]


# ==========================================================
# Service Configuration
# ==========================================================

@dataclass(frozen=True)
class ServiceConfig:

    name: str = field(
        default_factory=lambda:
        _env("SERVICE_NAME", "ASR AI Service")
    )

    version: str = field(
        default_factory=lambda:
        _env("SERVICE_VERSION", "1.0.0")
    )

    environment: str = field(
        default_factory=lambda:
        _env("SERVICE_ENVIRONMENT", "development")
    )


# ==========================================================
# Model Configuration
# ==========================================================

@dataclass(frozen=True)
class ModelConfig:

    name: str = field(
        default_factory=lambda:
        _env(
            "MODEL_NAME",
            "mohammedaly22/QwenCleo-ASR"
        )
    )

    device: str = field(
        default_factory=lambda:
        _env("MODEL_DEVICE", "auto")
    )

    trust_remote_code: bool = field(
        default_factory=lambda:
        _env_bool(
            "MODEL_TRUST_REMOTE_CODE",
            True
        )
    )


# ==========================================================
# Audio Configuration
# ==========================================================

@dataclass(frozen=True)
class AudioConfig:

    max_upload_size_mb: int = field(
        default_factory=lambda:
        _env_int(
            "ASR_MAX_UPLOAD_SIZE_MB",
            25
        )
    )

    supported_formats: list[str] = field(
        default_factory=lambda:
        _env_list(
            "ASR_SUPPORTED_FORMATS",
            "wav,mp3,flac,m4a,ogg,webm"
        )
    )


# ==========================================================
# Storage Configuration
# ==========================================================

@dataclass(frozen=True)
class StorageConfig:

    upload_dir: str = field(
        default_factory=lambda:
        _env(
            "ASR_UPLOAD_DIR",
            "/tmp/asr_uploads"
        )
    )


# ==========================================================
# Logging Configuration
# ==========================================================

@dataclass(frozen=True)
class LoggingConfig:

    level: str = field(
        default_factory=lambda:
        _env(
            "LOG_LEVEL",
            "INFO"
        )
    )


# ==========================================================
# RabbitMQ Configuration
# ==========================================================

@dataclass(frozen=True)
class RabbitMQConfig:

    host: str = field(
        default_factory=lambda:
        _env("RABBITMQ_HOST", "localhost")
    )

    port: int = field(
        default_factory=lambda:
        _env_int("RABBITMQ_PORT", 5672)
    )

    user: str = field(
        default_factory=lambda:
        _env("RABBITMQ_USER", "guest")
    )

    password: str = field(
        default_factory=lambda:
        _env("RABBITMQ_PASSWORD", "guest")
    )

    vhost: str = field(
        default_factory=lambda:
        _env("RABBITMQ_VHOST", "/")
    )

    requests_queue: str = field(
        default_factory=lambda:
        _env(
            "RABBITMQ_REQUESTS_QUEUE",
            "asr.transcription.requests"
        )
    )

    results_queue: str = field(
        default_factory=lambda:
        _env(
            "RABBITMQ_RESULTS_QUEUE",
            "asr.transcription.results"
        )
    )

    prefetch_count: int = field(
        default_factory=lambda:
        _env_int(
            "RABBITMQ_PREFETCH_COUNT",
            1
        )
    )


# ==========================================================
# Main Settings
# ==========================================================

@dataclass(frozen=True)
class Settings:

    service: ServiceConfig = field(
        default_factory=ServiceConfig
    )

    model: ModelConfig = field(
        default_factory=ModelConfig
    )

    audio: AudioConfig = field(
        default_factory=AudioConfig
    )

    storage: StorageConfig = field(
        default_factory=StorageConfig
    )

    logging: LoggingConfig = field(
        default_factory=LoggingConfig
    )

    rabbitmq: RabbitMQConfig = field(
        default_factory=RabbitMQConfig
    )


# ==========================================================
# Shared Settings Instance
# ==========================================================

settings = Settings()