"""
Enumerations for the Vision Service.
"""

from enum import Enum

class ProblemCode(str, Enum):
    """Problem types the AI can detect."""
    PIPE_DAMAGE = "Pipe_Damage"
    OVERFLOW = "Overflow"
    BLOCKAGE = "Blockage"

class SeverityLevel(str, Enum):
    """Severity levels for problems."""
    VERY_CRITICAL = "حرجة جداً"
    CRITICAL = "حرجة"
    VERY_HIGH = "عالية جداً"
    HIGH = "عالية"
    MEDIUM = "متوسطة"
    LOW = "منخفضة"
    MINOR = "بسيطة"
    VERY_MINOR = "بسيطة جداً"
    NEGLIGIBLE = "غير مؤثرة"
    UNKNOWN = "غير معروفة"

class StatusCode(str, Enum):
    """Response status codes."""
    SUCCESS = "success"
    LOW_CONFIDENCE = "low_confidence"
    POOR_QUALITY = "poor_quality"
    ERROR = "error"