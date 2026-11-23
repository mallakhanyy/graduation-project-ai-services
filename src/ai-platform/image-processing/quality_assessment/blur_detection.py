import numpy as np
from PIL import Image

from preprocessing.resize import resize_longest_side

BLUR_VARIANCE_MIN = 60.0   # below this the image is flagged "blurry"
SHARP_REFERENCE = 200.0    # variance considered fully sharp


def laplacian_variance(image: Image.Image, work_side: int = 512) -> float:
    """Variance of the Laplacian on a fixed working size (comparable across images)."""
    gray = np.asarray(resize_longest_side(image, work_side).convert("L"), dtype=np.float32)
    lap = (
        -4.0 * gray[1:-1, 1:-1]
        + gray[:-2, 1:-1] + gray[2:, 1:-1]
        + gray[1:-1, :-2] + gray[1:-1, 2:]
    )
    return float(lap.var())


def blur_score(image: Image.Image) -> tuple[float, bool]:
    """Return (score 0..1, is_blurry)."""
    var = laplacian_variance(image)
    return min(var / SHARP_REFERENCE, 1.0), var < BLUR_VARIANCE_MIN
