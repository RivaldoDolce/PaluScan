"""Statistiques inférentielles implémentées à la main, sans dépendance à scipy.

Chaque fonction est testée unitairement : intervalle de Wilson, AUC de
Mann-Whitney avec gestion des ex æquo, courbes ROC/PR, bootstrap percentile,
test exact de McNemar, courbe de calibration et valeurs prédictives de Bayes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalle de confiance de Wilson d'une proportion observée."""
    if total <= 0:
        raise ValueError("total doit être strictement positif")
    proportion = successes / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = (
        z * math.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2)) / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def auc_mann_whitney(scores: np.ndarray, labels: np.ndarray) -> float:
    """AUC au sens de l'U de Mann-Whitney, rangs moyens pour les ex æquo."""
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    n_pos = int(labels.sum())
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("les deux classes doivent être présentes")

    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    ranks = np.empty(len(scores), dtype=float)
    i = 0
    while i < len(scores):
        j = i
        while j + 1 < len(scores) and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j + 2) / 2.0
        i = j + 1

    rank_sum_pos = float(ranks[labels == 1].sum())
    u_pos = rank_sum_pos - n_pos * (n_pos + 1) / 2
    return float(u_pos / (n_pos * n_neg))


def roc_curve(scores: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Courbe ROC exacte par balayage décroissant des scores observés."""
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    order = np.argsort(-scores, kind="mergesort")
    sorted_labels = labels[order]
    sorted_scores = scores[order]

    n_pos = int(sorted_labels.sum())
    n_neg = len(sorted_labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("les deux classes doivent être présentes")

    tp = np.cumsum(sorted_labels)
    fp = np.cumsum(1 - sorted_labels)

    distinct = np.empty(len(scores), dtype=bool)
    distinct[-1] = True
    distinct[:-1] = sorted_scores[:-1] != sorted_scores[1:]

    fpr = np.concatenate(([0.0], fp[distinct] / n_neg))
    tpr = np.concatenate(([0.0], tp[distinct] / n_pos))
    thresholds = np.concatenate(([np.inf], sorted_scores[distinct]))
    return fpr, tpr, thresholds


def pr_curve(scores: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Courbe précision-rappel exacte par balayage décroissant des scores."""
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    order = np.argsort(-scores, kind="mergesort")
    sorted_labels = labels[order]
    sorted_scores = scores[order]

    n_pos = int(sorted_labels.sum())
    if n_pos == 0:
        raise ValueError("aucun exemple positif")

    tp = np.cumsum(sorted_labels)
    predicted_pos = np.arange(1, len(sorted_labels) + 1)
    recall = tp / n_pos
    precision = tp / predicted_pos

    distinct = np.empty(len(scores), dtype=bool)
    distinct[-1] = True
    distinct[:-1] = sorted_scores[:-1] != sorted_scores[1:]

    return precision[distinct], recall[distinct], sorted_scores[distinct]


def average_precision(scores: np.ndarray, labels: np.ndarray) -> float:
    """Précision moyenne, somme des gains de rappel pondérés par la précision."""
    precision, recall, _ = pr_curve(scores, labels)
    recall_prev = np.concatenate(([0.0], recall[:-1]))
    return float(np.sum((recall - recall_prev) * precision))


def bootstrap_ci(
    scores: np.ndarray,
    labels: np.ndarray,
    metric_fn,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float]:
    """Intervalle percentile d'une métrique par rééchantillonnage d'individus."""
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    rng = np.random.default_rng(seed)
    n = len(scores)
    estimates = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        estimates[b] = metric_fn(scores[idx], labels[idx])
    low, high = np.quantile(estimates, [alpha / 2, 1 - alpha / 2])
    return float(low), float(high)


@dataclass(frozen=True)
class McNemarResult:
    """Issue du test exact de McNemar sur deux modèles appariés."""

    b: int  # erreurs du modèle A uniquement
    c: int  # erreurs du modèle B uniquement
    n: int  # discordances totales
    p_value: float


def mcnemar_exact(errors_a: np.ndarray, errors_b: np.ndarray) -> McNemarResult:
    """Test exact de McNemar, p-valeur bilatérale sur la loi binomiale.

    Hypothèse nulle : les deux modèles se trompent avec la même fréquence sur
    les cas discordants.
    """
    errors_a = np.asarray(errors_a, dtype=bool)
    errors_b = np.asarray(errors_b, dtype=bool)
    b = int(np.sum(errors_a & ~errors_b))
    c = int(np.sum(~errors_a & errors_b))
    n = b + c
    if n == 0:
        return McNemarResult(b=b, c=c, n=0, p_value=1.0)
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return McNemarResult(b=b, c=c, n=n, p_value=float(min(1.0, 2 * tail)))


def calibration_curve(
    probs: np.ndarray, labels: np.ndarray, n_bins: int = 10
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fiabilité d'un score : confiance prédite et fréquence observée par intervalle.

    Renvoie (confiance moyenne par intervalle, taux observé, effectifs).
    """
    probs = np.asarray(probs, dtype=float)
    labels = np.asarray(labels, dtype=int)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.clip(np.digitize(probs, edges) - 1, 0, n_bins - 1)

    conf = np.zeros(n_bins)
    obs = np.zeros(n_bins)
    counts = np.zeros(n_bins, dtype=int)
    for b in range(n_bins):
        mask = bin_ids == b
        counts[b] = mask.sum()
        if counts[b] > 0:
            conf[b] = probs[mask].mean()
            obs[b] = labels[mask].mean()
    return conf, obs, counts


def youden_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    """Seuil opératoire maximisant l'indice J de Youden (sens + spéc - 1)."""
    fpr, tpr, thresholds = roc_curve(scores, labels)
    return float(thresholds[int(np.argmax(tpr - fpr))])


def ppv_npv(sensitivity: float, specificity: float, prevalence: float) -> tuple[float, float]:
    """Valeurs prédictives positive et négative par la formule de Bayes.

    Montre qu'un même test n'a pas la même valeur selon le contexte
    épidémiologique : un résultat positif ne « vaut » pas pareil quand la
    prévalence change.
    """
    if not 0 <= prevalence <= 1:
        raise ValueError("la prévalence doit être comprise entre 0 et 1")
    prev = prevalence
    ppv = (sensitivity * prev) / (sensitivity * prev + (1 - specificity) * (1 - prev))
    npv = (specificity * (1 - prev)) / (specificity * (1 - prev) + (1 - sensitivity) * prev)
    return float(ppv), float(npv)
