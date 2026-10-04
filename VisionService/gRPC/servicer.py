"""gRPC servicer — thin transport layer over Core.pipeline.analyze_image."""

import os
import uuid
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

import grpc
import requests

from gRPC import vision_pb2, vision_pb2_grpc
from Infrastructure.config import Settings, get_settings
from Infrastructure.image_fetcher import download_image_bytes, save_image_bytes
from Shared.exceptions import (
    VisionServiceException,
    ModelLoadError,
    ValidationError,
    PredictionError,
    PoorQualityError,
    NotIrrigationProblem,
    LowConfidenceError,
    UncertainPredictionError,
)

logger = logging.getLogger("VisionService.gRPC")

Analyzer = Callable[..., Dict[str, Any]]


def _default_analyzer() -> Analyzer:
    from Core.pipeline import analyze_image
    return analyze_image


def _default_health_probe() -> Tuple[bool, bool]:
    from Core.model import model
    from Core.binary_model import binary_classifier
    return model is not None, binary_classifier.model is not None


_EXCEPTION_STATUS = {
    ValidationError: grpc.StatusCode.INVALID_ARGUMENT,
    PoorQualityError: grpc.StatusCode.INVALID_ARGUMENT,
    NotIrrigationProblem: grpc.StatusCode.FAILED_PRECONDITION,
    LowConfidenceError: grpc.StatusCode.FAILED_PRECONDITION,
    UncertainPredictionError: grpc.StatusCode.FAILED_PRECONDITION,
    ModelLoadError: grpc.StatusCode.UNAVAILABLE,
    PredictionError: grpc.StatusCode.INTERNAL,
}


class VisionServicer(vision_pb2_grpc.VisionServiceServicer):

    def __init__(
        self,
        analyzer: Optional[Analyzer] = None,
        settings: Optional[Settings] = None,
        health_probe: Optional[Callable[[], Tuple[bool, bool]]] = None,
    ):
        self._analyzer = analyzer
        self._settings = settings or get_settings()
        self._health_probe = health_probe or _default_health_probe

    def _analyze(self, image_path, request_id):
        if self._analyzer is None:
            self._analyzer = _default_analyzer()
        return self._analyzer(image_path, settings=self._settings, request_id=request_id)

    def _run_bytes(self, data: bytes, request_id: str):
        path = save_image_bytes(data, self._settings)
        try:
            return self._analyze(path, request_id)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def Predict(self, request, context):
        request_id = request.request_id or uuid.uuid4().hex[:8]

        try:
            source = request.WhichOneof("source")
            if source == "image_data":
                data = request.image_data
            elif source == "image_url":
                data = download_image_bytes(request.image_url, self._settings)
            else:
                raise ValidationError("Set either image_data or image_url")

            logger.info(f"[{request_id}] Predict via {source} ({len(data)} bytes)")
            result = self._run_bytes(data, request_id)

            return vision_pb2.PredictResponse(
                status=result.get("status", "success"),
                problem=result.get("problem", ""),
                confidence=result.get("confidence", "0%"),
                severity=result.get("severity", ""),
                recommendation=result.get("recommendation", ""),
                explanation=result.get("explanation", ""),
                repair_steps=result.get("repair_steps", []),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
            )

        except requests.RequestException as exc:
            logger.warning(f"[{request_id}] Download failed: {exc}")
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                f"Could not download image: {exc}",
            )
        except VisionServiceException as exc:
            code = _EXCEPTION_STATUS.get(type(exc), grpc.StatusCode.INTERNAL)
            logger.info(f"[{request_id}] Rejected: {type(exc).__name__}: {exc}")
            context.abort(code, str(exc))
        except Exception as exc:
            logger.exception(f"[{request_id}] Unhandled error")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

    def HealthCheck(self, request, context):
        try:
            model_loaded, binary_loaded = self._health_probe()
        except Exception as exc:
            logger.error(f"Health probe failed: {exc}")
            model_loaded, binary_loaded = False, False

        return vision_pb2.HealthResponse(
            status="healthy" if model_loaded else "unhealthy",
            service=self._settings.SERVICE_NAME,
            version=self._settings.SERVICE_VERSION,
            model_loaded=model_loaded,
            binary_classifier_loaded=binary_loaded,
            timestamp=datetime.now().isoformat(),
        )