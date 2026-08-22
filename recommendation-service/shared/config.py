from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enums.vector_distance import VectorDistance


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int

    FILE_DEFAULT_CHUNK_SIZE: int
    FILE_CHUNK_OVERLAP: int

    MONGODB_URL: str
    MONGODB_DATABASE: str
    MONGODB_CHUNK_COLLECTION: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool
    MINIO_BUCKET_NAME: str

    EMBEDDING_MODEL_NAME: str
    EMBEDDING_NORMALIZE: bool

    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str
    QDRANT_DISTANCE: VectorDistance = VectorDistance.COSINE

    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SCORE_THRESHOLD: float = 0.60
    MAX_RECOMMENDATIONS: int = 3

    LLM_BASE_URL: str
    LLM_MODEL_NAME: str
    LLM_TEMPERATURE: float
    LLM_MAX_TOKENS: int
    LLM_TIMEOUT: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()