"""Static model configuration: label space, prompt templates, ensemble weights.

Keys are stable identifiers that match the backend ``ProblemCategory`` / agent
vocabulary; values are the natural-language descriptions fed to CLIP-style
models. Extend this dict (or load it from the knowledge base) as classes grow.
"""

PROBLEM_LABELS: dict[str, str] = {
    # keys are lower-case versions of the dataset folder names
    "pipe_damage": "a damaged, cracked, broken or leaking water pipe",
    "overflow": "water overflowing from a pipe, channel or tank and flooding the ground",
    "blockage": "a blocked pipe or drain clogged with dirt, debris or waste",
    "broken_channels": "a broken, cracked or collapsed irrigation channel or canal with damaged walls",
    "poor_irrigation_distribution": "an unevenly irrigated field with some dry areas and other areas flooded with water",
}


def normalize_label(folder_name: str) -> str:
    """'Broken Channels' / 'Broken-Channels' / 'Broken_Channels' -> 'broken_channels'."""
    return "_".join(folder_name.lower().replace("-", " ").replace("_", " ").split())

PROMPT_TEMPLATES: list[str] = [
    "a photo of {}.",
    "a close-up photo of {}.",
    "a photo taken on a farm showing {}.",
]

# Relative weight of each model when fusing per-model probabilities.
ENSEMBLE_WEIGHTS: dict[str, float] = {
    "clip": 1.0,
    "agriclip": 1.5,         # domain-tuned, trusted more
    "few_shot_probe": 1.25,  # trained on our own labelled farmer images
}

TTA_VIEWS_PER_IMAGE = 3