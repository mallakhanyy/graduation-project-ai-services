"""Measure vision accuracy on a folder-per-class dataset.

Dataset layout:   <root>/Pipe_Damage/*.jpg   <root>/Overflow/*.jpg   <root>/Blockage/*.jpg
Folder names (lower-cased) must match the keys of PROBLEM_LABELS.

Run from src/ai-platform/image-processing with PYTHONPATH=.;..  (Windows) :
    python ..\\..\\..\\research\\evaluation\\vision_metrics\\evaluate_zero_shot.py D:\\WahaKun\\waha_dataset --limit 30
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from services.vision_service import build_vision_service
from shared.configuration.model_config import PROBLEM_LABELS, normalize_label
from shared.configuration.settings import get_settings
from shared.contracts.vision_contract import VisionRequest, VisionStatus

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--limit", type=int, default=0, help="max images per class (0 = all)")
    ap.add_argument("--out", default="vision_eval_results.csv")
    ap.add_argument("--split-file", help="probe_split.json: evaluate ONLY its held-out test images")
    args = ap.parse_args()

    root = Path(args.dataset)
    classes = sorted(p for p in root.iterdir() if p.is_dir())
    unknown = [c.name for c in classes if normalize_label(c.name) not in PROBLEM_LABELS]
    if unknown:
        sys.exit(f"Folders not in PROBLEM_LABELS: {unknown}. Fix model_config.py or rename folders.")

    test_set = None
    if args.split_file:
        test_set = set(json.loads(Path(args.split_file).read_text(encoding="utf-8"))["test"])
        print(f"Held-out mode: {len(test_set)} test images only")

    settings = get_settings()
    settings.enable_captioning = False
    service = build_vision_service(settings)

    confusion: dict[str, Counter] = defaultdict(Counter)
    rows = []
    for cls in classes:
        truth = normalize_label(cls.name)
        files = sorted(f for f in cls.iterdir() if f.suffix.lower() in EXTS)
        if test_set is not None:
            files = [f for f in files if str(f.resolve()) in test_set]
        elif args.limit:
            files = files[: args.limit]
        for i, f in enumerate(files, 1):
            request = VisionRequest(query_id=f.name, bucket="", image_keys=[f.name])
            result = service.analyze(request, [(f.name, f.read_bytes())])
            pred = result.best_label if result.status == VisionStatus.COMPLETED else "rejected"
            confusion[truth][pred] += 1
            rows.append([str(f), truth, pred, result.confidence, result.status.value])
            print(f"\r{truth}: {i}/{len(files)}", end="", flush=True)
        print()

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([["file", "truth", "pred", "confidence", "status"], *rows])

    total = sum(sum(c.values()) for c in confusion.values())
    correct = sum(confusion[t][t] for t in confusion)
    rejected = sum(c["rejected"] for c in confusion.values())
    print(f"\nOverall accuracy: {correct}/{total} = {correct / max(total, 1):.1%}  (rejected by quality gate: {rejected})")
    cols = list(PROBLEM_LABELS) + ["rejected"]
    print("\nConfusion (rows = true class, columns = predicted):")
    w = max(len(c) for c in cols) + 2
    print(f"{'':{w}}" + "".join(f"{c:>{w}}" for c in cols))
    for t in confusion:
        print(f"{t:{w}}" + "".join(f"{confusion[t][c]:>{w}}" for c in cols))
    print(f"\nDetails saved to {args.out}")


if __name__ == "__main__":
    main()