from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All values can be overridden with SOSWAHA_* environment variables."""

    model_config = SettingsConfigDict(env_prefix="SOSWAHA_", env_file=".env", extra="ignore")

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    events_exchange: str = "soswaha.events"
    image_queue: str = "vision.query-submitted"
    query_submitted_routing_key: str = "query.submitted"
    vision_completed_routing_key: str = "vision.completed"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False

    # Image limits
    max_image_bytes: int = 10 * 1024 * 1024
    min_image_side: int = 96
    max_images_per_query: int = 5

    # Models
    device: str | None = None            # None -> cuda if available else cpu
    clip_model_name: str = "openai/clip-vit-base-patch16"
    agriclip_path: str | None = None     # local dir / HF id of a CLIP-compatible AgriCLIP checkpoint
    probe_path: str | None = None        # joblib file produced by research/ few-shot training
    enable_captioning: bool = True
    caption_model_name: str = "Salesforce/blip-image-captioning-base"

    # Behaviour
    quality_threshold: float = 0.45


@lru_cache
def get_settings() -> Settings:
    return Settings()
