import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

from shared.logging.logger import get_logger
from vision_models.clip.clip_loader import resolve_device

log = get_logger(__name__)


class ImageCaptioner:
    """BLIP captioner. Loaded lazily on first use. The caption is auxiliary
    evidence for the agent/fusion layer, not a primary classifier."""

    def __init__(self, model_name: str, device: str | None = None):
        self.model_name = model_name
        self.device = resolve_device(device)
        self._model = None
        self._processor = None

    def _ensure_loaded(self) -> None:
        if self._model is None:
            log.info("Loading captioner %s on %s", self.model_name, self.device)
            self._processor = BlipProcessor.from_pretrained(self.model_name)
            self._model = (
                BlipForConditionalGeneration.from_pretrained(self.model_name).to(self.device).eval()
            )

    @torch.inference_mode()
    def caption(self, image: Image.Image, max_new_tokens: int = 40) -> str:
        self._ensure_loaded()
        inputs = self._processor(images=image, text="a photo of", return_tensors="pt").to(self.device)
        out = self._model.generate(**inputs, max_new_tokens=max_new_tokens, num_beams=3)
        return self._processor.decode(out[0], skip_special_tokens=True).strip()
