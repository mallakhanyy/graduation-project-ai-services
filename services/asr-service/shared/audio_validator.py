from shared.config import settings

def validate_audio(audio_bytes: bytes, extension: str) -> None:

    extension = extension.lower().lstrip(".")

    if extension not in settings.audio.supported_formats:        
        raise ValueError(f"Unsupported audio format: {extension}")

    max_size_bytes = settings.audio.max_upload_size_mb * 1024 * 1024

    if len(audio_bytes) > max_size_bytes:
        raise ValueError(f"Audio file exceeds {settings.audio.max_upload_size_mb} MB.")