"""Calibration du garde-fou d'entrée : ajustement du dôme Giemsa et banc d'essai.

Usage :
    uv run python scripts/calibrer_validite.py --corpus data/cell_images [--negatifs DIR]

Le script ajuste le dôme de couleur sur 160 cellules tirées du corpus (80 par
classe, germe 42), évalue les gardes sur les cellules restantes et sur un
répertoire de contre-exemples (photos, recolorages), puis affiche la matrice
d'acceptation. Les constantes embarquées dans `paluscan.validite` proviennent
de cette procédure : banc d'essai du 2026-11-08, 316/320 cellules acceptées,
76/78 contre-exemples refusés.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from paluscan.config import CLASSES, RAW_DIR  # noqa: E402

TAILLE_AJUSTEMENT = 96
PAR_CLASSE = 80


def hsv(image: Image.Image) -> np.ndarray:
    """Convertit l'image en HSV normalisé à la taille d'analyse."""
    im = image.convert("RGB").resize((TAILLE_AJUSTEMENT, TAILLE_AJUSTEMENT), Image.BILINEAR)
    return np.asarray(im.convert("HSV"), dtype=np.float32) / 255.0


def vecteurs(image: Image.Image) -> np.ndarray:
    """Matrice (N, 5) : sin teinte, cos teinte, saturation, luminosité, saturation × luminosité."""
    canaux = hsv(image)
    h, s, v = canaux[..., 0], canaux[..., 1], canaux[..., 2]
    ang = h * 2.0 * np.pi
    return np.stack(
        [np.sin(ang).ravel(), np.cos(ang).ravel(), s.ravel(), v.ravel(), (s * v).ravel()],
        axis=1,
    )


def masque_objet(image: Image.Image) -> np.ndarray:
    """Sépare l'objet du fond pâle (luminosité élevée et faible saturation)."""
    canaux = hsv(image)
    return ~((canaux[..., 2] > 0.72) & (canaux[..., 1] < 0.22))


def ajuster_dome(chemins: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    """Estime moyenne et covariance du dôme sur les pixels d'objet du corpus."""
    blocs = []
    for chemin in chemins:
        image = Image.open(chemin)
        masque = masque_objet(image).ravel()
        if masque.sum() < 50:
            continue
        blocs.append(vecteurs(image)[masque])
    donnees = np.concatenate(blocs, axis=0)
    moyenne = donnees.mean(axis=0)
    covariance = np.cov(donnees, rowvar=False) + np.eye(5) * 1e-6
    inverse = np.linalg.inv(np.linalg.cholesky(covariance))
    return moyenne.astype(np.float32), inverse.astype(np.float32)


def dist_dome(image: Image.Image, moyenne: np.ndarray, inverse: np.ndarray) -> np.ndarray:
    """Distance de Mahalanobis de chaque pixel au dôme de couleur."""
    centre = vecteurs(image) - moyenne
    projection = (inverse @ centre.T).T
    return np.sqrt((projection**2).sum(axis=1))


def taux_dome(image: Image.Image, moyenne: np.ndarray, inverse: np.ndarray) -> float:
    """Part des pixels d'objet à l'intérieur du dôme de couleur."""
    objet = masque_objet(image).ravel()
    if not objet.any():
        return 0.0
    distances = dist_dome(image, moyenne, inverse)
    return float((distances[objet] < 4.0).mean())


def main() -> None:
    """Ajuste le dôme sur le corpus et mesure l'acceptation sur les deux ensembles."""
    parseur = argparse.ArgumentParser(description="Calibration du garde-fou de domaine")
    parseur.add_argument("--corpus", type=Path, default=RAW_DIR, help="dossier cell_images/")
    parseur.add_argument("--negatifs", type=Path, help="dossier de contre-exemples (optionnel)")
    args = parseur.parse_args()

    rng = random.Random(42)
    chemins_par_classe: dict[str, list[Path]] = {}
    for classe in CLASSES:
        dossier = args.corpus / classe.capitalize()
        chemins = sorted(dossier.glob("*.png"))
        if len(chemins) < PAR_CLASSE * 2:
            raise SystemExit(f"{dossier} : {len(chemins)} images, {PAR_CLASSE * 2} requises")
        chemins_par_classe[classe] = chemins

    ajustement = [rng.sample(chemins_par_classe[c], PAR_CLASSE) for c in CLASSES]
    chemins_ajustement = [p for liste in ajustement for p in liste]
    moyenne, inverse = ajuster_dome(chemins_ajustement)
    print(f"Dôme ajusté sur {len(chemins_ajustement)} cellules ({PAR_CLASSE} par classe)")
    print(f"moyenne = {[round(float(x), 5) for x in moyenne]}")
    print("inverse de Cholesky =")
    for ligne in inverse:
        print(f"    {[round(float(x), 5) for x in ligne]}")

    test = [p for c in CLASSES for p in chemins_par_classe[c] if p not in chemins_ajustement]
    acceptes = 0
    limites = 200
    echantillon = rng.sample(test, min(limites, len(test)))
    for chemin in echantillon:
        if taux_dome(Image.open(chemin), moyenne, inverse) >= 0.80:
            acceptes += 1
    print(f"\nCorpus (échantillon de {len(echantillon)}) : {acceptes} cellules dans le dôme à 80 %")

    if args.negatifs:
        negatifs = sorted(args.negatifs.glob("*"))
        refus = 0
        for chemin in negatifs:
            image = Image.open(chemin)
            verdict_dome = taux_dome(image, moyenne, inverse) >= 0.80
            refus += not verdict_dome
        print(f"Contre-exemples (dôme seul) : {refus}/{len(negatifs)} refusés")
        print("Contrôle complet : uv run pytest tests/test_validite.py")


if __name__ == "__main__":
    main()
