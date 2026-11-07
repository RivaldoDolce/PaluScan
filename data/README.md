# Récupération du corpus NIH

Le corpus d'images cellulaires n'est pas versionné dans le dépôt : il pèse
356 Mo et reste téléchargeable librement à la source. Ce dossier doit donc
être reconstitué une seule fois après le clonage du projet.

## Source

NIH / LSHTM, « Malaria Cell Images » — 27 558 cellules colorées au Giemsa,
64 × 64 px, réparties en deux classes équilibrées. Licence CC BY 4.0,
distribution officielle sur Mendeley Data.

- Fiche du jeu de données : <https://data.mendeley.com/datasets/y7z2vg7fmy/1>
- DOI : 10.17632/y7z2vg7fmy.1
- Archive directe (~356 Mo) :
  <https://data.mendeley.com/public-files/datasets/y7z2vg7fmy/files/4b1c12b1-e387-4400-ba02-5743ef46a3e5/file_downloaded>

Empreinte SHA-256 de l'archive officielle :

```
f8ee6f30deb46fb2c6dd8bee942eaf8401525bccf77ab7df6842a52adc14f768
```

## Intégration

```bash
curl -L -o /tmp/cell_images.zip \
  "https://data.mendeley.com/public-files/datasets/y7z2vg7fmy/files/4b1c12b1-e387-4400-ba02-5743ef46a3e5/file_downloaded"

sha256sum /tmp/cell_images.zip

uv run python scripts/prepare_data.py --archive /tmp/cell_images.zip
```

Le script décompresse l'archive dans `data/cell_images/Parasitized/` et
`data/cell_images/Uninfected/` (l'archive contient parfois un dossier racine
`cell_images/` qu'il aplatit automatiquement), puis :

1. vérifie la cohérence des classes et écrit `reports/dataset_audit.json` ;
2. reconstruit le découpage groupé par lame ;
3. rafraîchit les vignettes de démonstration dans
   `src/paluscan/app/static/img/exemples/`.

Valeurs attendues après audit : 27 558 cellules, 13 779 par classe,
comptage de lames et répartition des lots conformes à
`reports/dataset_audit.json` fourni.

## Ce qui fonctionne sans le corpus

- l'application : `uv run python -m paluscan.app` (les poids ONNX et les
  vignettes de démonstration sont versionnés) ;
- les tests : `uv run pytest` (jeux synthétiques) ;
- la CI GitHub Actions.

## Ce qui requiert le corpus

- l'audit complet : `uv run python scripts/prepare_data.py --archive ...` ;
- la baseline : `uv run python scripts/train_baseline.py` ;
- le réentraînement : `uv run python -m paluscan.train --epochs 16` ;
- l'évaluation et les figures : `uv run python -m paluscan.evaluate`.

## Référence d'origine

Publication NIH : <https://lhncbc.nlm.nih.gov/publication/pub9932>
(les téléchargements directs depuis ce domaine sont régulièrement
restreints ; le miroir Mendeley ci-dessus fait foi).
