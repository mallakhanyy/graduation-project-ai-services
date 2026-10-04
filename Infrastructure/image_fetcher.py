"""SSRF-safe image download and local save."""

import os
import socket
import uuid
import ipaddress
import logging
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError

from Infrastructure.config import Settings, get_settings

logger = logging.getLogger("VisionService.ImageFetcher")

_ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp", "bmp"}

# Hostnames always allowed (useful for local development).
_DEV_ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False

    # ---- DEV ONLY: allow localhost for local testing ----
    if parsed.hostname in _DEV_ALLOWED_HOSTS:
        return True
    # -----------------------------------------------------

    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
    except (socket.gaierror, ValueError):
        return False

    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _sniff_extension(data: bytes) -> str:
    try:
        img = Image.open(BytesIO(data))
        fmt = (img.format or "").lower()
        return {
            "jpeg": ".jpg",
            "png": ".png",
            "webp": ".webp",
            "bmp": ".bmp",
        }.get(fmt, ".jpg")
    except (UnidentifiedImageError, OSError):
        return ".jpg"


def download_image_bytes(image_url: str, settings: Settings = None) -> bytes:
    settings = settings or get_settings()

    if not _is_safe_url(image_url):
        raise ValueError(f"Refusing to download from unsafe URL: {image_url}")

    max_bytes = settings.MAX_FILE_SIZE
    timeout = (5, settings.IMAGE_DOWNLOAD_TIMEOUT)

    with requests.get(
        image_url, timeout=timeout, stream=True, allow_redirects=False
    ) as response:
        response.raise_for_status()

        declared = response.headers.get("Content-Length")
        if declared and declared.isdigit() and int(declared) > max_bytes:
            raise ValueError(f"Image exceeds {max_bytes} bytes (Content-Length)")

        total = 0
        buf = bytearray()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(f"Image exceeds {max_bytes} bytes")
            buf.extend(chunk)

    if not buf:
        raise ValueError("Empty response body")

    logger.info(f"Downloaded {total} bytes from {image_url}")
    return bytes(buf)


def save_image_bytes(data: bytes, settings: Settings = None) -> str:
    settings = settings or get_settings()

    if not data:
        raise ValueError("Empty image data")
    if len(data) > settings.MAX_FILE_SIZE:
        raise ValueError(
            f"حجم الملف كبير جداً. الحد الأقصى: "
            f"{settings.MAX_FILE_SIZE // (1024 * 1024)} ميجابايت"
        )

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    ext = _sniff_extension(data)
    filename = f"vision_{uuid.uuid4().hex[:12]}{ext}"
    path = os.path.join(settings.UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(data)

    return os.path.abspath(path)