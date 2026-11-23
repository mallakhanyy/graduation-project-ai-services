import time
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from PIL import Image

from captioning.caption_validator import validate_caption
from captioning.image_captioner import ImageCaptioner
from preprocessing.image_augmentation import generate_views
from preprocessing.resize import resize_longest_side
from quality_assessment.image_quality_score import advice_for, assess_quality
from shared.configuration.model_config import (
    ENSEMBLE_WEIGHTS, PROBLEM_LABELS, TTA_VIEWS_PER_IMAGE,
)
from shared.configuration.settings import Settings
from shared.contracts.vision_contract import (
    ImageQualityReport, LabelScore, ModelPrediction, VisionRequest, VisionResult, VisionStatus,
)
from shared.exceptions.errors import ImageTooSmallError, InvalidImageError
from shared.logging.logger import get_logger
from validation.image_validator import load_and_validate
from vision_models.agriclip.agriclip_loader import load_agriclip
from vision_models.agriclip.agriclip_predictor import AgriCLIPPredictor
from vision_models.clip.clip_loader import load_clip
from vision_models.clip.clip_predictor import ZeroShotCLIPPredictor
from vision_models.few_shot_probe.probe_loader import load_probe
from vision_models.few_shot_probe.probe_predictor import FewShotProbePredictor

log = get_logger(__name__)


@dataclass
class _Accepted:
    image: Image.Image
    report: ImageQualityReport


class VisionService:
    """validate -> quality gate -> TTA views -> CLIP / AgriCLIP / probe -> fuse -> caption."""

    def __init__(self, settings: Settings, clip: ZeroShotCLIPPredictor,
                 agriclip: AgriCLIPPredictor | None = None,
                 probe: FewShotProbePredictor | None = None,
                 captioner: ImageCaptioner | None = None):
        self.settings = settings
        self.clip = clip
        self.agriclip = agriclip
        self.probe = probe
        self.captioner = captioner

    # ------------------------------------------------------------------ public
    def analyze(self, request: VisionRequest, images: list[tuple[str, bytes]]) -> VisionResult:
        started = time.perf_counter()
        quality: list[ImageQualityReport] = []
        accepted: list[_Accepted] = []
        issues: list[str] = []
        too_small = 0

        for key, data in images:
            try:
                img = load_and_validate(
                    key, data,
                    max_bytes=self.settings.max_image_bytes,
                    min_side=self.settings.min_image_side,
                )
            except ImageTooSmallError as exc:
                log.warning("Too small %s: %s", key, exc)
                issues.append("low_resolution")
                too_small += 1
                continue
            except InvalidImageError as exc:
                log.warning("Rejected %s: %s", key, exc)
                issues.append("invalid_file")
                continue
            report = assess_quality(key, img, self.settings.quality_threshold)
            quality.append(report)
            issues.extend(report.issues)
            if report.is_acceptable:
                accepted.append(_Accepted(img, report))

        if not accepted:
            readable = bool(quality) or too_small > 0
            status = VisionStatus.LOW_QUALITY if readable else VisionStatus.FAILED
            return VisionResult(
                query_id=request.query_id,
                status=status,
                quality=quality,
                retake_advice=advice_for(issues, request.language),
                error=None if readable else "no valid image could be decoded",
                processing_ms=self._elapsed_ms(started),
            )

        labels = self._label_space(request.candidate_labels)
        views: list[Image.Image] = []
        for item in accepted:
            views.extend(generate_views(resize_longest_side(item.image, 1024), TTA_VIEWS_PER_IMAGE))

        predictions, embeddings = [], {}
        clip_pred, embeddings["clip"] = self.clip.predict(views)
        predictions.append(self._restrict(clip_pred, labels))

        if self.agriclip:
            agri_pred, embeddings["agriclip"] = self.agriclip.predict(views)
            predictions.append(self._restrict(agri_pred, labels))

        if self.probe and self.probe.embedding_source in embeddings:
            probe_pred = self.probe.predict_from_embeddings(embeddings[self.probe.embedding_source])
            predictions.append(self._restrict(probe_pred, labels))

        fused = self._fuse(predictions)
        margin = fused[0].score - fused[1].score if len(fused) > 1 else fused[0].score

        best = max(accepted, key=lambda a: a.report.quality_score)
        return VisionResult(
            query_id=request.query_id,
            status=VisionStatus.COMPLETED,
            quality=quality,
            model_predictions=predictions,
            fused_scores=fused[:5],
            best_label=fused[0].label,
            confidence=fused[0].score,
            margin=margin,
            caption=self._caption(best.image),
            retake_advice=advice_for(issues, request.language) if issues else [],
            processing_ms=self._elapsed_ms(started),
        )

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _label_space(candidates: list[str] | None) -> list[str]:
        if not candidates:
            return list(PROBLEM_LABELS)
        known = [c for c in candidates if c in PROBLEM_LABELS]
        return known or list(PROBLEM_LABELS)

    @staticmethod
    def _restrict(pred: ModelPrediction, labels: list[str]) -> ModelPrediction:
        """Keep only candidate labels and renormalise so scores sum to 1."""
        allowed = set(labels)
        kept = [s for s in pred.scores if s.label in allowed]
        total = sum(s.score for s in kept) or 1.0
        scores = [LabelScore(label=s.label, score=s.score / total) for s in kept]
        return ModelPrediction(
            model_name=pred.model_name, scores=scores,
            top_label=scores[0].label, confidence=scores[0].score,
        )

    @staticmethod
    def _fuse(predictions: list[ModelPrediction]) -> list[LabelScore]:
        """Weighted average of per-model probability distributions."""
        totals: dict[str, float] = defaultdict(float)
        weight_sum = 0.0
        for pred in predictions:
            w = ENSEMBLE_WEIGHTS.get(pred.model_name, 1.0)
            weight_sum += w
            for s in pred.scores:
                totals[s.label] += w * s.score
        fused = [LabelScore(label=l, score=v / weight_sum) for l, v in totals.items()]
        return sorted(fused, key=lambda s: s.score, reverse=True)

    def _caption(self, image: Image.Image) -> str | None:
        if not self.captioner:
            return None
        try:
            return validate_caption(self.captioner.caption(resize_longest_side(image, 512)))
        except Exception:  # noqa: BLE001 - captioning is optional evidence
            log.exception("Captioning failed; continuing without caption")
            return None

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return int((time.perf_counter() - started) * 1000)


def build_vision_service(settings: Settings) -> VisionService:
    """Composition root: load models once at startup."""
    labels = PROBLEM_LABELS
    clip = ZeroShotCLIPPredictor(load_clip(settings.clip_model_name, settings.device), labels)

    agri_bundle = load_agriclip(settings.agriclip_path, settings.device)
    agriclip = AgriCLIPPredictor(agri_bundle, labels) if agri_bundle else None

    probe_bundle = load_probe(settings.probe_path)
    if (
        probe_bundle
        and probe_bundle.clip_model_name
        and probe_bundle.clip_model_name != settings.clip_model_name
    ):
        # Same embedding size does not mean same embedding space: results would be garbage.
        log.error(
            "Probe was trained on %s but service uses %s; probe DISABLED. "
            "Set SOSWAHA_CLIP_MODEL_NAME=%s to use it.",
            probe_bundle.clip_model_name, settings.clip_model_name, probe_bundle.clip_model_name,
        )
        probe_bundle = None
    if probe_bundle and set(probe_bundle.labels) != set(PROBLEM_LABELS):
        # e.g. a 3-class probe used after new classes were added: it cannot predict them.
        log.error(
            "Probe classes %s differ from PROBLEM_LABELS %s; probe DISABLED. Retrain it.",
            sorted(probe_bundle.labels), sorted(PROBLEM_LABELS),
        )
        probe_bundle = None
    probe = FewShotProbePredictor(probe_bundle) if probe_bundle else None

    captioner = (
        ImageCaptioner(settings.caption_model_name, settings.device)
        if settings.enable_captioning else None
    )
    return VisionService(settings, clip, agriclip, probe, captioner)