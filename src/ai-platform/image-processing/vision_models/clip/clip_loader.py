from dataclasses import dataclass
from functools import lru_cache

import torch
from transformers import CLIPModel, CLIPProcessor

from shared.logging.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class CLIPBundle:
    name: str
    model: CLIPModel
    processor: CLIPProcessor
    device: str


def resolve_device(device: str | None = None) -> str:
    return device or ("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=4)
def load_clip(model_name_or_path: str, device: str | None = None) -> CLIPBundle:
    """Load (and cache) any CLIP-compatible checkpoint. Also used for AgriCLIP."""
    dev = resolve_device(device)
    log.info("Loading CLIP-compatible model %s on %s", model_name_or_path, dev)
    dtype = torch.float16 if dev == "cuda" else torch.float32
    model = CLIPModel.from_pretrained(model_name_or_path, torch_dtype=dtype).to(dev).eval()
    processor = CLIPProcessor.from_pretrained(model_name_or_path)
    return CLIPBundle(name=model_name_or_path, model=model, processor=processor, device=dev)
