from vision_models.clip.clip_loader import CLIPBundle
from vision_models.clip.clip_predictor import ZeroShotCLIPPredictor

# Domain-specific prompts suit an agriculture-tuned model better than generic ones.
AGRI_TEMPLATES = [
    "a photo of {}.",
    "a leaf image from a crop field showing {}.",
    "a smartphone photo taken by a farmer of {}.",
]


class AgriCLIPPredictor(ZeroShotCLIPPredictor):
    def __init__(self, bundle: CLIPBundle, labels: dict[str, str]):
        super().__init__(bundle, labels, model_name="agriclip", templates=AGRI_TEMPLATES)
