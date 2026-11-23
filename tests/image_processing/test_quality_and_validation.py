"""Run from src/ai-platform/image-processing with PYTHONPATH=.:..  (see README note)."""
import io

import numpy as np
import pytest
from PIL import Image, ImageFilter

from quality_assessment.image_quality_score import assess_quality
from shared.exceptions.errors import InvalidImageError, UnsupportedFormatError
from validation.image_validator import load_and_validate


def _jpeg(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


def _textured(size=640) -> Image.Image:
    rng = np.random.default_rng(0)
    return Image.fromarray(rng.integers(60, 200, (size, size, 3), dtype=np.uint8))


def test_valid_image_loads():
    img = load_and_validate("a.jpg", _jpeg(_textured()), max_bytes=10**7, min_side=160)
    assert img.mode == "RGB"


def test_wrong_content_rejected():
    with pytest.raises(UnsupportedFormatError):
        load_and_validate("a.jpg", b"not an image at all", max_bytes=10**7, min_side=160)


def test_too_small_rejected():
    with pytest.raises(InvalidImageError):
        load_and_validate("a.jpg", _jpeg(_textured(64)), max_bytes=10**7, min_side=160)


def test_sharp_image_acceptable_blurred_not():
    sharp = _textured()
    assert assess_quality("s", sharp).is_acceptable
    blurred = sharp.filter(ImageFilter.GaussianBlur(12))
    report = assess_quality("b", blurred)
    assert "blurry" in report.issues and not report.is_acceptable


def test_dark_image_flagged():
    dark = Image.new("RGB", (640, 640), (10, 10, 10))
    assert "too_dark" in assess_quality("d", dark).issues
