from datetime import datetime
from enum import Enum

from pydantic import Field

from shared.contracts.base import ContractModel


class ModalityType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"


class QuerySubmittedMessage(ContractModel):
    """Published by the backend (QuerySubmittedEvent) when a farmer submits a query."""

    query_id: str
    farmer_id: str
    modalities: list[ModalityType]
    bucket: str
    image_keys: list[str] = Field(default_factory=list)
    audio_key: str | None = None
    text: str | None = None
    language: str = "ar"
    crop: str | None = None
    submitted_at: datetime
