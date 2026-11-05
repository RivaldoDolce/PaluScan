"""Statistique inférentielle : exactitude des intervalles et des tests."""

import numpy as np

from paluscan.stats import (
    auc_mann_whitney,
    average_precision,
    bootstrap_ci,
    calibration_curve,
    mcnemar_exact,
    ppv_npv,
    roc_curve,
    wilson_interval,
    youden_threshold,
)


def test_wilson_interval_encadre_la_valeur():
    bas, haut = wilson_interval(successes=95, total=100)
    assert bas < 0.95 < haut
    assert 0 < bas < haut < 1


def test_wilson_interval_cas_extremes():
    bas, haut = wilson_interval(successes=0, total=10)
    assert bas == 0.0
    bas, haut = wilson_interval(successes=10, total=10)
    assert haut == 1.0


def test_auc_separe_parfaitement():
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    labels = np.array([0, 0, 1, 1])
    assert auc_mann_whitney(scores, labels) == 1.0


def test_auc_aleatoire_vaut_un_demi():
    rng = np.random.default_rng(0)
    scores = rng.uniform(size=400)
    labels = rng.integers(0, 2, size=400)
    assert abs(auc_mann_whitney(scores, labels) - 0.5) < 0.06


def test_roc_curve_points_cles():
    scores = np.array([0.1, 0.4, 0.35, 0.8])
    labels = np.array([0, 0, 1, 1])
    fpr, tpr, seuils = roc_curve(scores, labels)
    assert fpr[0] == 0.0 and tpr[0] == 0.0
    assert fpr[-1] == 1.0 and tpr[-1] == 1.0
    assert len(fpr) == len(tpr) == len(seuils)


def test_average_precision_ordre_informe():
    scores = np.array([0.9, 0.8, 0.2, 0.1])
    labels = np.array([1, 1, 0, 0])
    assert average_precision(scores, labels) == 1.0


def test_bootstrap_ci_serre_la_moyenne():
    rng = np.random.default_rng(1)
    echantillon = rng.normal(10.0, 1.0, size=500)
    bas, haut = bootstrap_ci(
        echantillon, np.zeros_like(echantillon), lambda s, _labels: s.mean(), n_boot=500, seed=1
    )
    assert bas < 10.0 < haut
    assert haut - bas < 0.4


def test_mcnemar_significatif_pour_un_seul_cote():
    erreurs_a = np.array([1] * 50 + [0] * 50)
    erreurs_b = np.array([0] * 50 + [1] * 5 + [0] * 45)
    resultat = mcnemar_exact(erreurs_a, erreurs_b)
    assert resultat.b == 50 and resultat.c == 5
    assert resultat.p_value < 0.05


def test_mcnemar_equilibre_non_significatif():
    rng = np.random.default_rng(7)
    erreurs_a = rng.binomial(1, 0.1, size=600)
    erreurs_b = rng.binomial(1, 0.1, size=600)
    resultat = mcnemar_exact(erreurs_a, erreurs_b)
    assert 0.0 <= resultat.p_value <= 1.0


def test_youden_threshold_separe_les_classes():
    scores = np.array([0.05, 0.1, 0.2, 0.7, 0.8, 0.9])
    labels = np.array([0, 0, 0, 1, 1, 1])
    seuil = youden_threshold(scores, labels)
    assert 0.2 < seuil <= 0.7


def test_ppv_npv_bayes():
    vpp, vpn = ppv_npv(sensitivity=1.0, specificity=1.0, prevalence=0.3)
    assert vpp == 1.0 and vpn == 1.0
    vpp, vpn = ppv_npv(sensitivity=0.9, specificity=0.9, prevalence=0.5)
    assert abs(vpp - 0.9) < 1e-9


def test_calibration_curve_bornes():
    rng = np.random.default_rng(3)
    scores = rng.uniform(size=1000)
    labels = (rng.uniform(size=1000) < scores).astype(int)
    confiance, observe, effectifs = calibration_curve(scores, labels, n_bins=10)
    assert len(confiance) == len(observe) == len(effectifs) == 10
    assert effectifs.sum() == 1000
    assert observe.min() >= 0.0 and observe.max() <= 1.0
