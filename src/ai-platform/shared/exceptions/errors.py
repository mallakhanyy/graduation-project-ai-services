class SosWahaError(Exception):
    """Base class for platform errors."""


class InvalidImageError(SosWahaError):
    """The file is not a usable image (bad type, corrupt, too small/large)."""


class ImageTooSmallError(InvalidImageError):
    """Readable image whose shortest side is below the configured minimum."""


class UnsupportedFormatError(InvalidImageError):
    """Extension or magic bytes are not an allowed image format."""


class ModelNotAvailableError(SosWahaError):
    """A required model could not be loaded."""