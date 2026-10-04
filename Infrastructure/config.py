"""Configuration management using environment variables."""

import os
from pathlib import Path
from typing import List
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "vision-service"
    SERVICE_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Model
    MODEL_PATH: str = "models/efficientnet_waha_kun.keras"
    BINARY_MODEL_PATH: str = "models/binary_classifier.keras"
    CONFIDENCE_THRESHOLD: float = 75.0
    BINARY_THRESHOLD: float = 0.75

    # Files
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]

    # Image Processing
    QUALITY_CHECK_ENABLED: bool = True
    ENHANCE_IMAGE_ENABLED: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    REQUESTS_QUEUE: str = "vision.analysis.request"
    RESULTS_QUEUE: str = "vision.analysis.result"

    # Image Download
    IMAGE_DOWNLOAD_TIMEOUT: int = 15

    # gRPC
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051
    GRPC_MAX_WORKERS: int = 10
    GRPC_MAX_MESSAGE_SIZE: int = 50 * 1024 * 1024
    GRPC_SHUTDOWN_GRACE: float = 10.0
    GRPC_ENABLE_REFLECTION: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()