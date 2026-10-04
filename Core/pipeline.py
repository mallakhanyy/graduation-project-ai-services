"""Single analysis pipeline used by REST, gRPC, and the Worker."""

import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from Core.model import predict_image
from Core.binary_model import is_irrigation_problem
from Core.knowledge_base import get_knowledge_recommendation
from Core.severity_enhanced import calculate_severity_enhanced
from Infrastructure.utils import check_image_quality, enhance_image
from Infrastructure.config import Settings, get_settings
from Shared.exceptions import (
    NotIrrigationProblem,
    LowConfidenceError,
    UncertainPredictionError,
    PoorQualityError,
)

logger = logging.getLogger("VisionService.Pipeline")

_UNCERTAIN_BAND = 85.0


def analyze_image(
    image_path: str,
    settings: Optional[Settings] = None,
    request_id: str = "unknown",
) -> Dict[str, Any]:
    """
    Returns:
        status, problem, confidence, severity, recommendation,
        explanation, repair_steps, timestamp

    Raises a VisionServiceException on any failure gate.
    """
    settings = settings or get_settings()
    enhanced_path: Optional[str] = None

    try:
        # 1) Quality gate
        if settings.QUALITY_CHECK_ENABLED:
            is_good, quality_msg = check_image_quality(image_path)
            if not is_good:
                logger.info(f"[{request_id}] Rejected: poor quality ({quality_msg})")
                raise PoorQualityError(quality_msg)

        # 2) Enhance
        image_to_predict = image_path
        if settings.ENHANCE_IMAGE_ENABLED:
            enhanced_path = enhance_image(image_path)
            if enhanced_path and enhanced_path != image_path:
                image_to_predict = enhanced_path
                logger.info(f"[{request_id}] Enhanced: {enhanced_path}")

        # 3) Predict
        result = predict_image(image_to_predict)
        english_class = result["problem_code"]
        confidence = float(result["confidence"])
        logger.info(f"[{request_id}] Predict: {english_class} ({confidence:.2f}%)")

        # 4) Binary gate
        is_problem, _binary_conf = is_irrigation_problem(
            image_to_predict, threshold=settings.BINARY_THRESHOLD
        )
        if not is_problem:
            logger.info(f"[{request_id}] Refused: not irrigation")
            raise NotIrrigationProblem("الصورة لا تظهر مشكلة ري واضحة.")

        # 5) Confidence gate
        if confidence < settings.CONFIDENCE_THRESHOLD:
            logger.info(f"[{request_id}] Low confidence: {confidence:.2f}%")
            raise LowConfidenceError(
                f"الثقة منخفضة ({confidence:.2f}%). يرجى رفع صورة أوضح"
            )

        # 6) Uncertain gate
        if confidence < _UNCERTAIN_BAND and english_class in {
            "Blockage", "Pipe_Damage", "Overflow"
        }:
            logger.info(f"[{request_id}] Uncertain: {english_class} @ {confidence:.2f}%")
            raise UncertainPredictionError(
                "تم اكتشاف مشكلة محتملة، لكن الصورة غير واضحة."
            )

        # 7) Success — no context passed
        recommendation = get_knowledge_recommendation(english_class, confidence)
        severity_result = calculate_severity_enhanced(english_class, confidence)

        return {
            "status": "success",
            "problem": recommendation.get("arabic", english_class),
            "confidence": f"{confidence:.2f}%",
            "severity": severity_result["level"],
            "recommendation": recommendation.get("recommendation", ""),
            "explanation": recommendation.get("explanation", "").strip(),
            "repair_steps": recommendation.get("steps", []),
            "timestamp": datetime.now().isoformat(),
        }

    finally:
        if enhanced_path and enhanced_path != image_path and os.path.exists(enhanced_path):
            try:
                os.remove(enhanced_path)
            except OSError:
                pass