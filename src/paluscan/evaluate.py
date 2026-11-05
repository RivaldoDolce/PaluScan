"""Évaluation complète du modèle sur le lot de test tenu à l'écart.

Produit reports/metrics.json (consommé par le tableau de bord de l'application)
ainsi que les figures statistiques du rapport. Usage :
uv run python -m paluscan.evaluate
"""

from __future__ import annotations

import json

import numpy as np
import torch
from torch.utils.data import DataLoader

from .config import BASELINE_PATH, METRICS_PATH, RAW_DIR, REPORTS_DIR, SEED, TORCH_PATH
from .data import discover, grouped_split
from .dataset import MalariaDataset
from .model import MalariaNet
from .stats import (
    auc_mann_whitney,
    average_precision,
    bootstrap_ci,
    calibration_curve,
    mcnemar_exact,
    pr_curve,
    roc_curve,
    wilson_interval,
    youden_threshold,
)


def accuracy_fn(scores: np.ndarray, labels: np.ndarray) -> float:
    """Exactitude au seuil 0,5, compatible avec la signature du bootstrap."""
    return float(((scores >= 0.5).astype(int) == labels).mean())


def sensitivity_at(scores: np.ndarray, labels: np.ndarray, threshold: float) -> float:
    """Taux de vrais positifs au seuil donné."""
    predicted = (scores >= threshold).astype(int)
    positives = labels == 1
    return float(predicted[positives].mean()) if positives.any() else 0.0


def specificity_at(scores: np.ndarray, labels: np.ndarray, threshold: float) -> float:
    """Taux de vrais négatifs au seuil donné."""
    predicted = (scores >= threshold).astype(int)
    negatives = labels == 0
    return float((1 - predicted[negatives]).mean()) if negatives.any() else 0.0


def downsample_curve(x: np.ndarray, y: np.ndarray, points: int = 60) -> list[list[float]]:
    """Réduit une courbe pour le rendu côté navigateur."""
    if len(x) <= points:
        return [[float(a), float(b)] for a, b in zip(x, y, strict=False)]
    idx = np.unique(np.linspace(0, len(x) - 1, points).astype(int))
    return [[float(x[i]), float(y[i])] for i in idx]


def evaluate(args=None) -> None:
    """Évalue le meilleur point de sauvegarde et écrit métriques et figures."""
    torch.manual_seed(SEED)
    torch.set_num_threads(2)

    records = discover(RAW_DIR)
    _, _, test_rec = grouped_split(records)
    test_set = MalariaDataset(test_rec)
    loader = DataLoader(test_set, batch_size=256, num_workers=2)

    checkpoint = torch.load(TORCH_PATH, weights_only=True)
    model = MalariaNet()
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    scores, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            scores.append(torch.softmax(model(x), dim=1)[:, 1].numpy())
            labels.append(y.numpy())
    scores = np.concatenate(scores)
    labels = np.concatenate(labels)

    threshold = youden_threshold(scores, labels)
    preds = (scores >= 0.5).astype(int)
    preds_youden = (scores >= threshold).astype(int)

    tp = int(((preds_youden == 1) & (labels == 1)).sum())
    fn = int(((preds_youden == 0) & (labels == 1)).sum())
    tn = int(((preds_youden == 0) & (labels == 0)).sum())
    fp = int(((preds_youden == 1) & (labels == 0)).sum())

    acc = accuracy_fn(scores, labels)
    sens = sensitivity_at(scores, labels, threshold)
    spec = specificity_at(scores, labels, threshold)
    auc = auc_mann_whitney(scores, labels)
    ap = average_precision(scores, labels)

    metrics: dict = {
        "n_test": int(len(labels)),
        "n_test_slides": len({r.slide for r in test_rec}),
        "n_train": None,
        "n_val": None,
        "seuil_youden": round(float(threshold), 4),
        "exactitude": {
            "valeur": round(acc, 4),
            "ic95": [round(v, 4) for v in bootstrap_ci(scores, labels, accuracy_fn, n_boot=1000)],
            "wilson": [round(v, 4) for v in wilson_interval(tp + tn, len(labels))],
        },
        "sensibilite": {
            "valeur": round(sens, 4),
            "ic95": [
                round(v, 4)
                for v in bootstrap_ci(
                    scores, labels, lambda s, lb: sensitivity_at(s, lb, threshold), n_boot=1000
                )
            ],
            "wilson": [round(v, 4) for v in wilson_interval(tp, tp + fn)],
        },
        "specificite": {
            "valeur": round(spec, 4),
            "ic95": [
                round(v, 4)
                for v in bootstrap_ci(
                    scores, labels, lambda s, lb: specificity_at(s, lb, threshold), n_boot=1000
                )
            ],
            "wilson": [round(v, 4) for v in wilson_interval(tn, tn + fp)],
        },
        "auc": {
            "valeur": round(auc, 4),
            "ic95": [
                round(v, 4) for v in bootstrap_ci(scores, labels, auc_mann_whitney, n_boot=1000)
            ],
        },
        "precision_moyenne": round(ap, 4),
        "matrice_confusion": {"vp": tp, "fn": fn, "vn": tn, "fp": fp},
    }

    fpr, tpr, _ = roc_curve(scores, labels)
    precision, recall, _ = pr_curve(scores, labels)
    conf, obs, counts = calibration_curve(scores, labels)
    roc_points = downsample_curve(fpr, tpr)
    pr_points = downsample_curve(recall, precision)
    metrics["roc"] = {"fpr": [p[0] for p in roc_points], "tpr": [p[1] for p in roc_points]}
    metrics["pr"] = {"rappel": [p[0] for p in pr_points], "precision": [p[1] for p in pr_points]}
    metrics["calibration"] = {
        "confiance": [round(float(c), 4) for c in conf],
        "observe": [round(float(o), 4) for o in obs],
        "effectifs": [int(c) for c in counts],
    }

    # Comparaison appariée avec la baseline si ses prédictions sont disponibles.
    base_scores: np.ndarray | None = None
    if BASELINE_PATH.exists():
        saved = np.load(BASELINE_PATH, allow_pickle=False)
        base_scores = saved["baseline_scores"]
        base_labels = saved["labels"]
        assert np.array_equal(base_labels, labels), "lots de test divergents entre baseline et CNN"
        err_cnn = (preds != labels).astype(bool)
        err_base = ((base_scores >= 0.5).astype(int) != labels).astype(bool)
        result = mcnemar_exact(err_base, err_cnn)
        base_acc = accuracy_fn(base_scores, base_labels)
        metrics["baseline"] = {
            "nom": "PCA(50) + régression logistique",
            "exactitude": round(base_acc, 4),
            "auc": round(auc_mann_whitney(base_scores, base_labels), 4),
        }
        metrics["mcnemar"] = {
            "b_base_seulement": result.b,
            "c_cnn_seulement": result.c,
            "n_discordantes": result.n,
            "p_value": round(result.p_value, 6),
            "significatif_5pc": bool(result.p_value < 0.05),
        }

    history_path = REPORTS_DIR / "history.json"
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
        metrics["entrainement"] = {
            "epoques": [h["epoch"] for h in history],
            "perte_train": [round(h["train_loss"], 4) for h in history],
            "perte_val": [round(h["val_loss"], 4) for h in history],
            "auc_val": [round(h["val_auc"], 4) for h in history],
            "meilleure_epoque": max(history, key=lambda h: h["val_auc"])["epoch"],
        }

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Test : {len(labels)} cellules / {metrics['n_test_slides']} lames")
    print(f"Exactitude {acc:.4f} | sensibilité {sens:.4f} | spécificité {spec:.4f} | AUC {auc:.4f}")
    print(f"Seuil de Youden retenu : {threshold:.3f}")
    print(f"Métriques écrites dans {METRICS_PATH}")


if __name__ == "__main__":
    evaluate()
