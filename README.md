---
title: PaluScan
emoji: C
sdk: docker
app_port: 7860
license: mit
short_description: Détection du paludisme sur frottis sanguins par un CNN léger
---

# PaluScan

Détection du paludisme sur frottis sanguins minces par un réseau convolutif léger,
avec explicabilité par occlusion, statistique inférentielle écrite à la main et
application web interactive (FastHTML + ONNXRuntime).

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088ff)](#deploiement)

## Résultats (jeu de test, 4 082 cellules issues de 212 lames)

| Métrique | Valeur | IC 95 % (bootstrap, 10 000 tirages) |
| --- | --- | --- |
| AUC ROC | 0,9914 | [0,989 ; 0,994] |
| Sensibilité | 96,8 % | [96,0 ; 97,5] |
| Spécificité | 95,4 % | [94,5 ; 96,3] |
| Exactitude | 96,0 % | [95,3 ; 96,6] |

Décision au seuil de Youden (0,4875), test de McNemar contre la baseline
PCA(50) + régression logistique : p &lt; 0,001. Courbes ROC, précision–rappel,
calibration et matrice de confusion exposées sur la page `/methode`.

## Points méthodologiques

- **Découpage par lame** : les cellules d'une même lame ne sont jamais réparties
  entre entraînement, validation et test — élimine la fuite statistique qui gonfle
  artificiellement les métriques sur ce jeu.
- **Garde-fou d'entrée** : tout upload passe un contrôle statistique (dôme de couleur
  Giemsa par distance de Mahalanobis, saturation, grain, bords, matière, fond) — une photo
  ou une capture d'écran est refusée avec ses motifs, jamais diagnostiquée.
- **MalariaNet** : 3 blocs convolutifs (32/64/128) + tête dense, 62 000 paramètres,
  entraîné sur 2 cœurs CPU avec augmentation et arrêt anticipé (16 époques).
- **Statistique sans dépendance** : Wilson, ROC, bootstrap stratifié, McNemar exact
  et calibration implémentés dans un unique module NumPy (`src/paluscan/stats.py`).
- **Explicabilité** : cartes d'occlusion 8×8 (pas de 4) servies avec chaque prédiction.
- **Inférence ONNX** : PyTorch absent du conteneur de démonstration, latence &lt; 10 ms.

## Démarrage rapide

```bash
uv sync                     # installe l'environnement (Python 3.12)
uv run python -m paluscan.app   # application sur http://localhost:7860
```

Pages : `/` (accueil), `/demo` (laboratoire d'analyse), `/methode` (tableau de bord).

### Réentraînement complet

```bash
uv run python scripts/prepare_data.py --archive /tmp/cell_images.zip
uv run python scripts/train_baseline.py
uv run python -m paluscan.train --epochs 16
uv run python scripts/export_onnx.py
uv run python -m paluscan.evaluate
```

Les poids ONNX et les métriques de référence sont déjà versionnés
(`models/paluscan.onnx`, `reports/metrics.json`) : l'application fonctionne
sans réentraîner.

## Structure

```
src/paluscan/
  data.py        découverte du corpus et découpage groupé par lame
  dataset.py     chargement, normalisation, augmentation
  model.py       MalariaNet (PyTorch)
  train.py       boucle d'entraînement, arrêt anticipé, reprise
  stats.py       Wilson, ROC, PR, bootstrap, McNemar, calibration, Youden
  evaluate.py    métriques du jeu de test, courbes, rapport JSON
  explain.py     cartes d'occlusion via ONNXRuntime
  predict.py     encapsulation d'inférence
  validite.py    garde-fou de domaine : contrôle Giemsa avant toute prédiction
  config.py      chemins et constantes
  app/           FastHTML : vues, routes, statiques (CSS/JS/fonts)
tests/           pytest : statistique, découpage, garde-fou, inférence, application
scripts/         préparation des données, baseline, export ONNX
```

## Tests et qualité

```bash
uv run pytest          # 42 tests
uv run ruff check .    # lint
uv run ruff format .   # format
```

La CI GitHub Actions exécute lint, format et tests à chaque poussée.

## Déploiement

L'image Docker écoute sur le port 7860 et fonctionne telle quelle sur
Hugging Face Spaces (sdk `docker`) : pousser le dépôt dans un Space.
L'en-tête YAML du présent README déclare la configuration requise.

## Données et licence

- Corpus NIH / LSHTM « Malaria Cell Images » (27 558 cellules, 64×64, Giemsa),
  distribué sous licence CC BY 4.0 via Mendeley Data (doi : 10.17632/y7z2vg7fmy).
- Code : MIT (voir `LICENSE`).

PaluScan est un projet d'étude : aucune décision médicale ne doit s'appuyer
sur ses sorties.
