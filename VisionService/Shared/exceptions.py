"""Custom exceptions for the Vision Service."""


class VisionServiceException(Exception):
    """Base exception for Vision Service."""
    pass


class ModelLoadError(VisionServiceException):
    pass


class ImageProcessingError(VisionServiceException):
    pass


class ValidationError(VisionServiceException):
    pass


class PredictionError(VisionServiceException):
    pass


class PoorQualityError(VisionServiceException):
    pass


class NotIrrigationProblem(VisionServiceException):
    pass


class LowConfidenceError(VisionServiceException):
    pass


class UncertainPredictionError(VisionServiceException):
    pass