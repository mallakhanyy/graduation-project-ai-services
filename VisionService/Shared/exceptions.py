"""
Custom exceptions for the Vision Service.
"""

class VisionServiceException(Exception):
    """Base exception for Vision Service."""
    pass

class ModelLoadError(VisionServiceException):
    """Raised when the AI model fails to load."""
    pass

class ImageProcessingError(VisionServiceException):
    """Raised when image processing fails."""
    pass

class ValidationError(VisionServiceException):
    """Raised when input validation fails."""
    pass

class PredictionError(VisionServiceException):
    """Raised when prediction fails."""
    pass