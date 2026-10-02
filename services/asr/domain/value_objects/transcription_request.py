from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptionRequest:
    request_id: str
    audio_url: str
    extension: str