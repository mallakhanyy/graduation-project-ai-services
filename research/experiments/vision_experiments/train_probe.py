"""Train a few-shot linear probe on frozen CLIP embeddings of YOUR dataset.

Why: zero-shot CLIP relies on text descriptions only. The probe learns from your real
photos, which usually fixes the weak classes (e.g. pipe_damage).

Honest evaluation: images are split into train / test. Zero-shot CLIP and the probe are
both scored on the SAME held-out test images the probe never saw.

Run from src/ai-platform/image-processing with PYTHONPATH=.;..  (Windows):
    python ..\\..\\..\\research\\experiments\\vision_experiments\\train_probe.py D:\\WahaKun\\waha_dataset

Outputs (in --out-dir, default ./probe_output):
    probe.joblib       the trained probe (loaded by the service via SOSWAHA_PROBE_PATH)
    probe_split.json   which images were used for train / test
"""
import argparse
import json
import re
import sys
import warnings
from math import sqrt
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from PIL import Image, ImageOps
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold, train_test_split

from preprocessing.image_augmentation import generate_views
from preprocessing.resize import resize_longest_side
from shared.configuration.model_config import PROBLEM_LABELS, TTA_VIEWS_PER_IMAGE, normalize_label
from vision_models.clip.clip_loader import load_clip
from vision_models.clip.clip_predictor import ZeroShotCLIPPredictor

warnings.filterwarnings("ignore", category=FutureWarning)  # noisy sklearn notices

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def collect(root: Path, limit: int) -> tuple[list[Path], list[str]]:
    paths, labels = [], []
    for cls in sorted(p for p in root.iterdir() if p.is_dir()):
        label = normalize_label(cls.name)
        if label not in PROBLEM_LABELS:
            sys.exit(f"Folder '{cls.name}' is not in PROBLEM_LABELS (model_config.py)")
        files = sorted(f for f in cls.iterdir() if f.suffix.lower() in EXTS)
        for f in (files[:limit] if limit else files):
            paths.append(f.resolve())
            labels.append(label)
    return paths, labels


def embed_images(predictor, paths: list[Path], cache_file: Path) -> tuple[list[Path], np.ndarray]:
    """One embedding per image, built exactly like the service does at inference time:
    mean of the TTA-view embeddings, re-normalised. Cached so re-runs are fast."""
    cache: dict[str, np.ndarray] = {}
    if cache_file.exists():
        data = np.load(cache_file, allow_pickle=False)
        cache = dict(zip(data["paths"].tolist(), data["emb"]))

    ok_paths, rows = [], []
    for i, p in enumerate(paths, 1):
        key = str(p)
        if key not in cache:
            try:
                img = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
            except Exception as exc:  # noqa: BLE001
                print(f"\nskip unreadable {p.name}: {exc}")
                continue
            views = generate_views(resize_longest_side(img, 1024), TTA_VIEWS_PER_IMAGE)
            e = predictor.embed(views).mean(0)
            cache[key] = e / (np.linalg.norm(e) + 1e-12)
        ok_paths.append(p)
        rows.append(cache[key])
        print(f"\rembedding {i}/{len(paths)}", end="", flush=True)
    print()
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache_file, paths=np.array(list(cache)), emb=np.stack(list(cache.values())))
    return ok_paths, np.stack(rows)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson confidence interval for a proportion."""
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d


def print_confusion(y_true, y_pred, classes, title: str) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    w = max(len(c) for c in classes) + 2
    print(f"\n{title} (rows = true, columns = predicted):")
    print(f"{'':{w}}" + "".join(f"{c:>{w}}" for c in classes))
    for c, row in zip(classes, cm):
        print(f"{c:{w}}" + "".join(f"{v:>{w}}" for v in row))


def cross_validate(emb, y, predictor, k: int, seed: int) -> None:
    """Stratified k-fold: every image is predicted once by a probe that never saw it.
    Much more reliable than a single split when some classes have few images."""
    classes = sorted(set(y))
    k = min(k, min(Counter(y).values()))
    if k < 2:
        print("Cross-validation skipped: a class has fewer than 2 images.")
        return
    oof = np.empty(len(y), dtype=object)
    for tr, te in StratifiedKFold(n_splits=k, shuffle=True, random_state=seed).split(emb, y):
        inner = max(2, min(5, min(Counter(y[tr]).values())))
        clf = LogisticRegressionCV(
            Cs=[0.1, 1, 10, 100], cv=inner, max_iter=5000, class_weight="balanced"
        ).fit(emb[tr], y[tr])
        oof[te] = clf.predict(emb[te])
    zero = np.array([predictor.predict_from_embeddings(e[None]).top_label for e in emb])

    print(f"\n=== {k}-fold cross-validation on ALL {len(y)} images ===")
    for name, pred in (("zero-shot CLIP", zero), ("probe (out-of-fold)", oof)):
        correct = int((pred == y).sum())
        lo, hi = wilson(correct, len(y))
        per = recall_by_class(y, pred, classes)
        print(f"\n{name}: {correct}/{len(y)} = {correct / len(y):.1%}   95% CI [{lo:.1%}, {hi:.1%}]")
        for c in classes:
            n = int((y == c).sum())
            print(f"   {c}: {per[c]:.0%} ({int(round(per[c] * n))}/{n})")
    print_confusion(y, oof, classes, "Probe out-of-fold confusion")


def recall_by_class(y_true, y_pred, classes) -> dict[str, float]:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return {c: float((y_pred[y_true == c] == c).mean()) for c in classes}


def run(args, predictor) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths, labels = collect(Path(args.dataset), args.limit)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.model)
    paths, emb = embed_images(predictor, paths, out_dir / f"embeddings_{slug}.npz")
    y = np.array([normalize_label(p.parent.name) for p in paths])
    classes = sorted(set(y))

    print("\nImages per class:", dict(Counter(map(str, y))))
    if args.cross_val:
        cross_validate(emb, y, predictor, args.cross_val, args.seed)

    idx = np.arange(len(y))
    train_idx, test_idx = train_test_split(
        idx, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    cv = min(5, min(Counter(y[train_idx]).values()))
    if cv < 2:
        sys.exit("Need at least 2 training images per class.")

    clf = LogisticRegressionCV(
        Cs=[0.1, 1, 10, 100], cv=cv, max_iter=5000, class_weight="balanced"
    ).fit(emb[train_idx], y[train_idx])

    probe_pred = clf.predict(emb[test_idx])
    zero_pred = [predictor.predict_from_embeddings(emb[i][None]).top_label for i in test_idx]
    y_test = y[test_idx]

    print(f"\ntrain images: {len(train_idx)}   held-out test images: {len(test_idx)}")
    for name, pred in (("zero-shot CLIP", zero_pred), ("probe", probe_pred)):
        acc = float((np.asarray(pred) == y_test).mean())
        per = recall_by_class(y_test, pred, classes)
        print(f"\n{name}: accuracy {acc:.1%}")
        print("   " + "  ".join(f"{c}: {v:.0%}" for c, v in per.items()))

    cm = confusion_matrix(y_test, probe_pred, labels=classes)
    print("\nProbe confusion on test (rows = true, columns = predicted):")
    w = max(len(c) for c in classes) + 2
    print(f"{'':{w}}" + "".join(f"{c:>{w}}" for c in classes))
    for c, row in zip(classes, cm):
        print(f"{c:{w}}" + "".join(f"{v:>{w}}" for v in row))

    if args.fit_all:
        clf = LogisticRegressionCV(
            Cs=[0.1, 1, 10, 100], cv=cv, max_iter=5000, class_weight="balanced"
        ).fit(emb, y)
        print("\n--fit-all: final probe retrained on ALL images (cannot be evaluated honestly afterwards).")

    probe_file = out_dir / "probe.joblib"
    joblib.dump(
        {
            "classifier": clf,
            "labels": [str(c) for c in clf.classes_],
            "embedding_source": "clip",
            "clip_model_name": args.model,
        },
        probe_file,
    )
    (out_dir / "probe_split.json").write_text(
        json.dumps(
            {
                "model": args.model,
                "train": [str(paths[i]) for i in train_idx],
                "test": [str(paths[i]) for i in test_idx],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nSaved {probe_file}")
    print("To use it:")
    print(f'  $env:SOSWAHA_PROBE_PATH = "{probe_file.resolve()}"')
    print(f'  $env:SOSWAHA_CLIP_MODEL_NAME = "{args.model}"')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--model", default="openai/clip-vit-base-patch16")
    ap.add_argument("--limit", type=int, default=0, help="max images per class (0 = all)")
    ap.add_argument("--test-size", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", default="probe_output")
    ap.add_argument("--cross-val", type=int, default=0, metavar="K",
                    help="also report K-fold cross-validated accuracy on all images (recommended: 5)")
    ap.add_argument("--fit-all", action="store_true",
                    help="after reporting, retrain on all images for the shipped probe")
    args = ap.parse_args()
    predictor = ZeroShotCLIPPredictor(load_clip(args.model), PROBLEM_LABELS, model_name="clip")
    run(args, predictor)


if __name__ == "__main__":
    main()