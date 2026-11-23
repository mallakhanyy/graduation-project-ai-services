"""Fusion ablation: does fusing zero-shot CLIP with the probe help, and with what weight?

Honest protocol (the test set of Experiments E/F is NOT used):
  * the probe's probabilities are OUT-OF-FOLD (stratified k-fold, repeated with different shuffles),
    i.e. every image is scored by a probe that never saw it;
  * zero-shot CLIP needs no training, so its probabilities are used as they are;
  * fused = (w_clip * P_clip + w_probe * P_probe) / (w_clip + w_probe)   -- exactly what VisionService does;
  * w_probe is fixed at the service value; w_clip is varied. w_clip = 0 is "probe only".

It evaluates the classifiers only (no input validation / quality gate).

Run from src/ai-platform/image-processing with PYTHONPATH=.;..  (Windows):
    python ..\\..\\..\\research\\experiments\\vision_experiments\\fusion_ablation.py D:\\WahaKun\\waha_dataset --out-dir probe_output_5class
(--out-dir = the folder holding embeddings_*.npz written by train_probe.py; reusing it avoids re-embedding.)
"""
import argparse
import re
import warnings
from collections import Counter
from math import comb
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold

from shared.configuration.model_config import ENSEMBLE_WEIGHTS, PROBLEM_LABELS, normalize_label
from train_probe import collect, embed_images, wilson
from vision_models.clip.clip_loader import load_clip
from vision_models.clip.clip_predictor import ZeroShotCLIPPredictor

warnings.filterwarnings("ignore", category=FutureWarning)

CLIP_WEIGHTS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]


def zero_shot_probs(predictor, emb: np.ndarray, classes: list[str]) -> np.ndarray:
    cidx = {c: i for i, c in enumerate(classes)}
    out = np.zeros((len(emb), len(classes)))
    for i, e in enumerate(emb):
        for s in predictor.predict_from_embeddings(e[None]).scores:
            if s.label in cidx:
                out[i, cidx[s.label]] = s.score
    return out / out.sum(axis=1, keepdims=True)  # renormalise over the dataset's classes


def oof_probe_probs(emb, y_idx, classes, k: int, seed: int) -> np.ndarray:
    out = np.zeros((len(emb), len(classes)))
    for tr, te in StratifiedKFold(n_splits=k, shuffle=True, random_state=seed).split(emb, y_idx):
        inner = max(2, min(5, min(Counter(y_idx[tr]).values())))
        clf = LogisticRegressionCV(
            Cs=[0.1, 1, 10, 100], cv=inner, max_iter=5000, class_weight="balanced"
        ).fit(emb[tr], y_idx[tr])
        out[np.ix_(te, clf.classes_)] = clf.predict_proba(emb[te])
    return out


def metrics(P: np.ndarray, y_idx: np.ndarray, n_classes: int) -> dict:
    pred = P.argmax(1)
    recalls = np.array([(pred[y_idx == c] == c).mean() for c in range(n_classes)])
    logloss = float(-np.log(np.clip(P[np.arange(len(y_idx)), y_idx], 1e-12, 1)).mean())
    return {"acc": float((pred == y_idx).mean()), "bal": float(recalls.mean()),
            "ll": logloss, "recalls": recalls, "correct": pred == y_idx}


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar test on the discordant pairs b (A right, B wrong) and c."""
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def run(args, predictor) -> None:
    out_dir = Path(args.out_dir)
    paths, _ = collect(Path(args.dataset), 0)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.model)
    paths, emb = embed_images(predictor, paths, out_dir / f"embeddings_{slug}.npz")
    y = np.array([normalize_label(p.parent.name) for p in paths])
    classes = sorted(set(y))
    cidx = {c: i for i, c in enumerate(classes)}
    y_idx = np.array([cidx[v] for v in y])
    n = len(y)
    k = min(args.k, min(Counter(y_idx).values()))
    w_probe = ENSEMBLE_WEIGHTS["few_shot_probe"]
    w_current = ENSEMBLE_WEIGHTS["clip"]

    print(f"\n{n} images, classes: {dict(Counter(map(str, y)))}")
    print(f"{k}-fold CV repeated {args.repeats}x; probe weight = {w_probe}; current CLIP weight = {w_current}")

    P_clip = zero_shot_probs(predictor, emb, classes)
    P_probe = [oof_probe_probs(emb, y_idx, classes, k, args.seed + r) for r in range(args.repeats)]

    rows = []
    for wc in CLIP_WEIGHTS:
        ms = [metrics((wc * P_clip + w_probe * Pp) / (wc + w_probe), y_idx, len(classes)) for Pp in P_probe]
        rows.append((f"probe + CLIP (w_clip={wc:g})", wc, ms))
    rows.append(("CLIP only (zero-shot)", None, [metrics(P_clip, y_idx, len(classes))] * args.repeats))

    print(f"\n{'configuration':32}{'accuracy (mean ± sd)':>24}{'balanced acc':>15}{'log-loss':>11}")
    for name, wc, ms in rows:
        acc = np.array([m["acc"] for m in ms])
        bal = np.mean([m["bal"] for m in ms])
        ll = np.mean([m["ll"] for m in ms])
        tag = "   <- current service setting" if wc == w_current else ""
        print(f"{name:32}{acc.mean():>16.1%} ± {acc.std():.1%}{bal:>15.1%}{ll:>11.3f}{tag}")

    print("\nPer-class recall (mean over repeats):")
    w = max(len(c) for c in classes) + 2
    print(f"{'':32}" + "".join(f"{c[:w - 1]:>{w}}" for c in classes))
    for name, wc, ms in rows:
        if wc in (0.0, w_current, None):
            rec = np.mean([m["recalls"] for m in ms], axis=0)
            print(f"{name:32}" + "".join(f"{r:>{w}.0%}" for r in rec))

    print("\nPaired comparison with probe-only (repeat 1 only, so images are independent):")
    base = rows[0][2][0]["correct"]
    for name, wc, ms in rows[1:-1]:
        cur = ms[0]["correct"]
        b = int((base & ~cur).sum())  # probe-only right, fusion wrong
        c = int((~base & cur).sum())  # probe-only wrong, fusion right
        print(f"  {name:28} fusion fixes {c:>2}, fusion breaks {b:>2}, exact McNemar p = {mcnemar_exact(b, c):.3f}")

    best = max(rows[:-1], key=lambda r: np.mean([m["acc"] for m in r[2]]))
    k_ok = int(round(np.mean([m["acc"] for m in best[2]]) * n))
    lo, hi = wilson(k_ok, n)
    print(f"\nHighest mean accuracy: {best[0]} ({k_ok}/{n}, 95% CI [{lo:.1%}, {hi:.1%}]).")
    print("Note: choosing the best of several weights on these same images is optimistic; "
          "if you change the weights, confirm on new images.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--model", default="openai/clip-vit-base-patch16")
    ap.add_argument("--out-dir", default="probe_output")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    predictor = ZeroShotCLIPPredictor(load_clip(args.model), PROBLEM_LABELS, model_name="clip")
    run(args, predictor)


if __name__ == "__main__":
    main()