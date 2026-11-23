import numpy as np

from shared.contracts.vision_contract import LabelScore, ModelPrediction
from vision_models.few_shot_probe.probe_loader import ProbeBundle


class FewShotProbePredictor:
    model_name = "few_shot_probe"

    def __init__(self, bundle: ProbeBundle):
        self.bundle = bundle

    @property
    def embedding_source(self) -> str:
        return self.bundle.embedding_source

    def predict_from_embeddings(self, embeddings: np.ndarray) -> ModelPrediction:
        mean = embeddings.mean(axis=0)
        mean = mean / (np.linalg.norm(mean) + 1e-12)
        probs = self.bundle.classifier.predict_proba(mean.reshape(1, -1))[0]
        scores = sorted(
            (LabelScore(label=l, score=float(p)) for l, p in zip(self.bundle.labels, probs)),
            key=lambda s: s.score,
            reverse=True,
        )
        return ModelPrediction(
            model_name=self.model_name,
            scores=scores,
            top_label=scores[0].label,
            confidence=scores[0].score,
        )
