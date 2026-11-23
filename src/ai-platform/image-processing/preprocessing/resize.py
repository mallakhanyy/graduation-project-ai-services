from PIL import Image


def resize_longest_side(image: Image.Image, max_side: int = 1024) -> Image.Image:
    """Downscale (never upscale) so the longest side is at most ``max_side``."""
    longest = max(image.size)
    if longest <= max_side:
        return image
    scale = max_side / longest
    new_size = (round(image.width * scale), round(image.height * scale))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def resize_square(image: Image.Image, size: int = 224, mode: str = "pad") -> Image.Image:
    """Return a size x size image.

    mode="pad":  keep the whole image, letterbox with neutral grey.
    mode="crop": centre-crop (what CLIP's own preprocessing does).
    """
    if mode == "crop":
        side = min(image.size)
        left, top = (image.width - side) // 2, (image.height - side) // 2
        return image.crop((left, top, left + side, top + side)).resize(
            (size, size), Image.Resampling.BICUBIC
        )
    scale = size / max(image.size)
    resized = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.BICUBIC,
    )
    canvas = Image.new("RGB", (size, size), (128, 128, 128))
    canvas.paste(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
    return canvas
