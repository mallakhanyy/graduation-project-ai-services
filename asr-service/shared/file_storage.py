from pathlib import Path

from shared.config import settings
from shared.logger import logger


def get_audio_path(request_id: str, extension: str) -> str:
    upload_dir = Path(settings.storage.upload_dir)

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    audio_path = upload_dir / f"{request_id}.{extension}"

    return str(audio_path)


def delete_audio(audio_path: str) -> None:

    logger.info(
        f"Deleting temporary audio: {audio_path}"
    )

    audio_file = Path(audio_path)

    if audio_file.exists():
        audio_file.unlink()

        logger.info(
            f"Temporary audio deleted: {audio_path}"
        )
    else:
        logger.warning(
            f"Temporary audio not found: {audio_path}"
        )