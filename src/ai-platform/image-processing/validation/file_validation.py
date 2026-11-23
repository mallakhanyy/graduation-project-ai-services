from pathlib import PurePath

from shared.exceptions.errors import InvalidImageError, UnsupportedFormatError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def detect_format(data: bytes) -> str | None:
    """Detect the real format from magic bytes (never trust the extension alone)."""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def validate_file(filename: str, data: bytes, max_bytes: int) -> str:
    """Cheap pre-decode checks. Returns the detected format."""
    if not data:
        raise InvalidImageError(f"{filename}: empty file")
    if len(data) > max_bytes:
        raise InvalidImageError(f"{filename}: {len(data)} bytes exceeds limit of {max_bytes}")
    ext = PurePath(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFormatError(f"{filename}: extension '{ext}' not allowed")
    fmt = detect_format(data)
    if fmt is None:
        raise UnsupportedFormatError(f"{filename}: content is not a supported image")
    return fmt
