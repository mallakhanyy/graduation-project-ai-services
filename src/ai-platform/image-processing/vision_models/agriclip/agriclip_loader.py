from shared.logging.logger import get_logger
from vision_models.clip.clip_loader import CLIPBundle, load_clip

log = get_logger(__name__)


def load_agriclip(path: str | None, device: str | None = None) -> CLIPBundle | None:
    """Load the AgriCLIP checkpoint (a CLIP-compatible, agriculture fine-tuned model).

    Returns None when no checkpoint is configured or loading fails, so the
    pipeline degrades gracefully to CLIP (+ probe) instead of crashing.
    """
    if not path:
        log.info("AgriCLIP not configured; skipping")
        return None
    try:
        return load_clip(path, device)
    except Exception:  # noqa: BLE001
        log.exception("Failed to load AgriCLIP from %s; continuing without it", path)
        return None
