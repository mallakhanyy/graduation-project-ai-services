"""Configuration management using Pydantic Settings."""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "Arabic Comment Moderation Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Model
    model_path: str = "app/infrastructure/model/WAHA_KUN_AraBERT"
    max_sequence_length: int = 128
    device: Literal["cpu", "cuda"] = "cpu"
    confidence_threshold: float = 0.7
    
    # RabbitMQ
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "moderation_queue"
    rabbitmq_results_queue: str = "results_queue"  # ← NEW
    rabbitmq_heartbeat: int = 600
    rabbitmq_timeout: int = 300
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["text", "json"] = "text"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=('settings_',),
    )


settings = Settings()