import numpy as np
from PIL import Image

from preprocessing.resize import resize_square

CLIP_MEAN = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
CLIP_STD = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)


def to_normalized_array(image: Image.Image, size: int = 224, mode: str = "crop") -> np.ndarray:
    """CHW float32 array normalised with CLIP statistics.

    The HF processors do this internally; this exists for ONNX/TensorRT
    backends and for research notebooks that bypass the processor.
    """
    arr = np.asarray(resize_square(image, size, mode), dtype=np.float32) / 255.0
    arr = (arr - CLIP_MEAN) / CLIP_STD
    return arr.transpose(2, 0, 1)
