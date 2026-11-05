"""Baseline interprétable : PCA sur pixels aplatis puis régression logistique.

Sert de point de comparaison apparié (test exact de McNemar) au CNN. Usage :
uv run python scripts/train_baseline.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paluscan.config import BASELINE_PATH, IMG_SIZE, RAW_DIR, SEED  # noqa: E402
from paluscan.data import discover, grouped_split  # noqa: E402


def featurise(records: list) -> np.ndarray:
    """Aplati les images en niveaux de gris redimensionnés."""
    out = np.empty((len(records), IMG_SIZE * IMG_SIZE), dtype=np.float32)
    for i, record in enumerate(records):
        with Image.open(record.path) as img:
            gray = img.convert("L").resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
        out[i] = np.asarray(gray, dtype=np.float32).ravel() / 255.0
    return out


def main() -> None:
    """Entraîne la baseline PCA + régression logistique et enregistre ses prédictions."""
    started = time.perf_counter()
    records = discover(RAW_DIR)
    train, _, test = grouped_split(records)

    rng = np.random.default_rng(SEED)
    if len(train) > 12000:
        idx = rng.choice(len(train), size=12000, replace=False)
        train = [train[i] for i in idx]

    x_train = featurise(train)
    x_test = featurise(test)
    y_train = np.array([r.label for r in train])
    y_test = np.array([r.label for r in test])

    model = make_pipeline(
        StandardScaler(),
        PCA(n_components=50, random_state=SEED),
        LogisticRegression(max_iter=2000, C=0.1),
    )
    model.fit(x_train, y_train)
    scores = model.predict_proba(x_test)[:, 1]

    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(BASELINE_PATH, baseline_scores=scores, labels=y_test)
    acc = float(((scores >= 0.5).astype(int) == y_test).mean())
    print(f"Baseline entraînée : exactitude test {acc:.4f} ({time.perf_counter() - started:.0f} s)")
    print(f"Prédictions écrites dans {BASELINE_PATH}")


if __name__ == "__main__":
    main()
