"""
Constants used across the Vision Service.
"""

# ============================================
# Service Constants
# ============================================
SERVICE_NAME = "vision-service"
SERVICE_VERSION = "1.0.0"

# ============================================
# Problem Types
# ============================================
PROBLEM_TYPES = {
    "Pipe_Damage": {
        "code": "Pipe_Damage",
        "arabic": "تلف في أنبوب المياه",
        "severity_levels": ["حرجة جداً", "حرجة", "عالية", "متوسطة", "منخفضة"]
    },
    "Overflow": {
        "code": "Overflow",
        "arabic": "فيض في المياه",
        "severity_levels": ["عالية جداً", "عالية", "متوسطة", "منخفضة", "بسيطة"]
    },
    "Blockage": {
        "code": "Blockage",
        "arabic": "انسداد في قناة الري",
        "severity_levels": ["متوسطة", "منخفضة", "بسيطة", "بسيطة جداً", "غير مؤثرة"]
    }
}

# ============================================
# Image Processing Constants
# ============================================
TARGET_SIZE = (224, 224)
MIN_IMAGE_SIZE = (100, 100)
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================
# Confidence Thresholds
# ============================================
CONFIDENCE_THRESHOLD = 50.0
HIGH_CONFIDENCE = 70.0
VERY_HIGH_CONFIDENCE = 85.0