from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # ==========================================================
    # Service Configuration
    # ==========================================================
    SERVICE_NAME: str = "ASR AI Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_ENVIRONMENT: str = "development"

    # ==========================================================
    # Model Configuration
    # ==========================================================
    MODEL_NAME: str = "mohammedaly22/QwenCleo-ASR"
    MODEL_DEVICE: str = "auto"
    MODEL_TRUST_REMOTE_CODE: bool = True

    # ==========================================================
    # Audio Configuration
    # ==========================================================
    ASR_MAX_UPLOAD_SIZE_MB: int = 25
    ASR_SUPPORTED_FORMATS: str = "wav,mp3,flac,m4a,ogg,webm"

    # ==========================================================
    # Storage Configuration
    # ==========================================================
    ASR_UPLOAD_DIR: str = "/tmp/asr_uploads"

    # ==========================================================
    # Logging Configuration
    # ==========================================================
    LOG_LEVEL: str = "INFO"

    # ==========================================================
    # RabbitMQ Configuration
    # ==========================================================
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_REQUESTS_QUEUE: str = "asr.transcription.requests"
    RABBITMQ_RESULTS_QUEUE: str = "asr.transcription.results"
    RABBITMQ_PREFETCH_COUNT: int = 1

    # ==========================================================
    # API Configuration
    # ==========================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ==========================================================
    # Pydantic Config
    # ==========================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Shared Settings Instance
settings = Settings()