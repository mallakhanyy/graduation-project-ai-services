from datetime import datetime, timezone
from enum import Enum

from pydantic import Field

from shared.contracts.base import ContractModel


class VisionStatus(str, Enum):
    COMPLETED = "completed"
    LOW_QUALITY = "low_quality"  # images readable but unusable -> ask farmer to retake
    FAILED = "failed"            # technical failure (storage, corrupt file, model error)


class ImageQualityReport(ContractModel):
    image_key: str
    width: int
    height: int
    blur_score: float        # 0 (blurry) .. 1 (sharp)
    brightness_score: float  # 0 (bad exposure) .. 1 (ideal)
    quality_score: float     # weighted 0..1
    is_acceptable: bool
    issues: list[str] = Field(default_factory=list)  # blurry | too_dark | too_bright | low_resolution


class LabelScore(ContractModel):
    label: str
    score: float


class ModelPrediction(ContractModel):
    model_name: str  # clip | agriclip | few_shot_probe
    scores: list[LabelScore]
    top_label: str
    confidence: float


class VisionRequest(ContractModel):
    query_id: str
    bucket: str
    image_keys: list[str]
    language: str = "ar"
    candidate_labels: list[str] | None = None  # restrict the label space (e.g. by crop)


class VisionResult(ContractModel):
    query_id: str
    status: VisionStatus
    quality: list[ImageQualityReport] = Field(default_factory=list)
    model_predictions: list[ModelPrediction] = Field(default_factory=list)
    fused_scores: list[LabelScore] = Field(default_factory=list)
    best_label: str | None = None
    confidence: float | None = None
    margin: float | None = None  # top1 - top2, a cheap ambiguity signal for fusion
    caption: str | None = None
    retake_advice: list[str] = Field(default_factory=list)
    error: str | None = None
    processing_ms: int = 0
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
