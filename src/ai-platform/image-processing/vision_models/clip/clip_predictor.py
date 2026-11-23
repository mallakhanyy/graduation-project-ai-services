import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from shared.configuration.model_config import PROMPT_TEMPLATES
from shared.contracts.vision_contract import LabelScore, ModelPrediction
from vision_models.clip.clip_loader import CLIPBundle


def _as_tensor(features) -> torch.Tensor:
    """transformers >= 5 returns BaseModelOutputWithPooling (projected features in
    ``pooler_output``); older versions return the tensor directly."""
    return features if isinstance(features, torch.Tensor) else features.pooler_output


class ZeroShotCLIPPredictor:
    """Zero-shot classifier: image embedding vs. prompt-ensembled label embeddings.

    AgriCLIP reuses this class (see agriclip_predictor) because it is a
    CLIP-compatible checkpoint.
    """

    def __init__(self, bundle: CLIPBundle, labels: dict[str, str],
                 model_name: str = "clip", templates: list[str] | None = None):
        self.bundle = bundle
        self.labels = labels
        self.model_name = model_name
        self.templates = templates or PROMPT_TEMPLATES
        self._text_emb: torch.Tensor | None = None

    @torch.inference_mode()
    def _text_embeddings(self) -> torch.Tensor:
        if self._text_emb is None:
            rows = []
            for description in self.labels.values():
                prompts = [t.format(description) for t in self.templates]
                tokens = self.bundle.processor(
                    text=prompts, return_tensors="pt", padding=True
                ).to(self.bundle.device)
                emb = F.normalize(_as_tensor(self.bundle.model.get_text_features(**tokens)), dim=-1).mean(0)
                rows.append(F.normalize(emb, dim=-1))
            self._text_emb = torch.stack(rows)
        return self._text_emb

    @torch.inference_mode()
    def embed(self, images: list[Image.Image]) -> np.ndarray:
        """L2-normalised image embeddings, shape (n, d)."""
        inputs = self.bundle.processor(images=images, return_tensors="pt").to(self.bundle.device)
        pixel_values = inputs["pixel_values"].to(self.bundle.model.dtype)
        emb = F.normalize(
            _as_tensor(self.bundle.model.get_image_features(pixel_values=pixel_values)), dim=-1
        )
        return emb.float().cpu().numpy()

    @torch.inference_mode()
    def predict_from_embeddings(self, embeddings: np.ndarray) -> ModelPrediction:
        """Average view embeddings, then softmax over cosine similarities."""
        mean = F.normalize(torch.from_numpy(embeddings).mean(0), dim=-1).to(self.bundle.device)
        text = self._text_embeddings().to(mean.dtype)
        scale = self.bundle.model.logit_scale.exp().float().item()
        probs = torch.softmax(scale * (text @ mean), dim=-1).cpu().numpy()

        scores = sorted(
            (LabelScore(label=l, score=float(p)) for l, p in zip(self.labels, probs)),
            key=lambda s: s.score,
            reverse=True,
        )
        return ModelPrediction(
            model_name=self.model_name,
            scores=scores,
            top_label=scores[0].label,
            confidence=scores[0].score,
        )

    def predict(self, images: list[Image.Image]) -> tuple[ModelPrediction, np.ndarray]:
        embeddings = self.embed(images)
        return self.predict_from_embeddings(embeddings), embeddings
