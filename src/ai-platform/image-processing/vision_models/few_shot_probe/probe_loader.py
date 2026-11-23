from dataclasses import dataclass
from pathlib import Path

import joblib

from shared.logging.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class ProbeBundle:
    classifier: object            # sklearn estimator exposing predict_proba
    labels: list[str]             # class order of classifier.classes_
    embedding_source: str         # "clip" | "agriclip": which embeddings it was trained on
    clip_model_name: str | None = None  # exact checkpoint the embeddings came from


def load_probe(path: str | None) -> ProbeBundle | None:
    """Load a linear probe trained on frozen image embeddings (few-shot).

    Expected joblib payload:
        {"classifier": LogisticRegression, "labels": [...], "embedding_source": "clip"}
    """
    if not path or not Path(path).exists():
        log.info("Few-shot probe not configured or missing; skipping")
        return None
    payload = joblib.load(path)
    return ProbeBundle(
        classifier=payload["classifier"],
        labels=list(payload["labels"]),
        embedding_source=payload.get("embedding_source", "clip"),
        clip_model_name=payload.get("clip_model_name"),
    )