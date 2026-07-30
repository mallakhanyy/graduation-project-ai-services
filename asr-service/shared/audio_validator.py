from shared.config import settings


def validate_extension(extension: str) -> str:
    extension = extension.lower().lstrip(".")

    if extension not in settings.audio.supported_formats:
        raise ValueError(
            f"Unsupported audio format: {extension}"
        )

    return extension