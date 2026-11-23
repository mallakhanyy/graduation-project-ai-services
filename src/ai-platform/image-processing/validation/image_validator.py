import io

from PIL import Image, ImageOps, UnidentifiedImageError

from shared.exceptions.errors import ImageTooSmallError, InvalidImageError
from validation.file_validation import validate_file

# Guards against decompression bombs (~50 MP).
Image.MAX_IMAGE_PIXELS = 50_000_000


def load_and_validate(filename: str, data: bytes, *, max_bytes: int, min_side: int) -> Image.Image:
    """Validate bytes, decode, fix EXIF orientation and return an RGB image."""
    validate_file(filename, data, max_bytes)
    try:
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()  # structural integrity check; invalidates the handle
        image = Image.open(io.BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise InvalidImageError(f"{filename}: cannot decode image ({exc})") from exc

    image = ImageOps.exif_transpose(image)  # phone photos are often rotated via EXIF
    if image.mode != "RGB":
        image = image.convert("RGB")

    if min(image.size) < min_side:
        raise ImageTooSmallError(
            f"{filename}: {image.width}x{image.height} is below minimum side of {min_side}px"
        )
    return image