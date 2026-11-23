import numpy as np
from PIL import Image

from preprocessing.resize import resize_longest_side

IDEAL_LOW, IDEAL_HIGH = 90.0, 170.0
TOO_DARK_MEAN, TOO_BRIGHT_MEAN = 60.0, 200.0


def brightness_stats(image: Image.Image) -> tuple[float, float, float]:
    """Return (mean luma 0..255, fraction of near-black pixels, fraction of near-white pixels)."""
    gray = np.asarray(resize_longest_side(image, 256).convert("L"), dtype=np.float32)
    return float(gray.mean()), float((gray < 30).mean()), float((gray > 225).mean())


def brightness_score(image: Image.Image) -> tuple[float, bool, bool]:
    """Return (score 0..1, too_dark, too_bright)."""
    mean, dark_frac, bright_frac = brightness_stats(image)
    if mean < IDEAL_LOW:
        score = mean / IDEAL_LOW
    elif mean > IDEAL_HIGH:
        score = (255.0 - mean) / (255.0 - IDEAL_HIGH)
    else:
        score = 1.0
    # Heavy clipping hurts even when the mean looks fine (backlit / flash glare).
    score *= 1.0 - 0.5 * max(dark_frac, bright_frac)
    too_dark = mean < TOO_DARK_MEAN or dark_frac > 0.6
    too_bright = mean > TOO_BRIGHT_MEAN or bright_frac > 0.6
    return max(0.0, min(score, 1.0)), too_dark, too_bright
