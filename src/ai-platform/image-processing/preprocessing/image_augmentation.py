import random

from PIL import Image, ImageEnhance


def generate_views(image: Image.Image, n_views: int = 3) -> list[Image.Image]:
    """Deterministic test-time-augmentation views (original first).

    Averaging embeddings across mild views makes predictions more robust to
    framing and lighting in farmer-taken photos.
    """
    views = [image]
    candidates = [
        lambda im: im.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
        lambda im: ImageEnhance.Contrast(im).enhance(1.15),
        lambda im: im.rotate(8, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=(128, 128, 128)),
        lambda im: im.transpose(Image.Transpose.FLIP_TOP_BOTTOM),
    ]
    for fn in candidates[: max(0, n_views - 1)]:
        views.append(fn(image))
    return views


def random_augment(image: Image.Image, seed: int | None = None) -> Image.Image:
    """Random augmentation for training / few-shot probe data expansion."""
    rng = random.Random(seed)
    if rng.random() < 0.5:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    image = image.rotate(rng.uniform(-20, 20), resample=Image.Resampling.BICUBIC, fillcolor=(128, 128, 128))
    image = ImageEnhance.Brightness(image).enhance(rng.uniform(0.8, 1.2))
    image = ImageEnhance.Color(image).enhance(rng.uniform(0.85, 1.15))
    return image
