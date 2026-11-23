"""Compare several CLIP-compatible models on the same folder-per-class dataset.

Run from src/ai-platform/image-processing with PYTHONPATH=.;..  (Windows):
    python ..\\..\\..\\research\\evaluation\\vision_metrics\\compare_clip_models.py ^
        D:\\WahaKun\\waha_dataset --limit 30 ^
        --models openai/clip-vit-base-patch16 openai/clip-vit-large-patch14

Each --models value is a Hugging Face id or a local folder holding a
transformers-format CLIP checkpoint.
"""
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageOps

from shared.configuration.model_config import PROBLEM_LABELS, normalize_label
from vision_models.clip.clip_loader import load_clip
from vision_models.clip.clip_predictor import ZeroShotCLIPPredictor

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def load_samples(root: Path, limit: int) -> list[tuple[Path, str]]:
    samples = []
    for cls in sorted(p for p in root.iterdir() if p.is_dir()):
        truth = normalize_label(cls.name)
        if truth not in PROBLEM_LABELS:
            sys.exit(f"Folder '{cls.name}' is not in PROBLEM_LABELS (model_config.py)")
        files = sorted(f for f in cls.iterdir() if f.suffix.lower() in EXTS)
        samples += [(f, truth) for f in (files[:limit] if limit else files)]
    return samples


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    samples = load_samples(Path(args.dataset), args.limit)
    print(f"{len(samples)} images, classes: {list(PROBLEM_LABELS)}\n")

    summary = []
    for spec in args.models:
        try:
            predictor = ZeroShotCLIPPredictor(load_clip(spec), PROBLEM_LABELS, model_name=spec)
        except Exception as exc:  # noqa: BLE001
            print(f"!! could not load {spec}: {exc}\n")
            continue
        per_class: dict[str, Counter] = defaultdict(Counter)
        for i, (path, truth) in enumerate(samples, 1):
            img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
            pred, _ = predictor.predict([img])
            per_class[truth][pred.top_label] += 1
            print(f"\r{spec}: {i}/{len(samples)}", end="", flush=True)
        print()
        correct = sum(per_class[t][t] for t in per_class)
        summary.append((spec, correct / len(samples), {t: per_class[t][t] / sum(per_class[t].values()) for t in per_class}))

    print("\n=== Results ===")
    for spec, acc, by_class in summary:
        detail = "  ".join(f"{t}: {v:.0%}" for t, v in by_class.items())
        print(f"{acc:6.1%}  {spec}\n        {detail}")


if __name__ == "__main__":
    main()