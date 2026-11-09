"""Garde-fou d'entrée : vérifie qu'une image ressemble à un frottis coloré au Giemsa.

Le dôme de couleur est ajusté hors ligne sur 160 cellules du corpus (80 parasitées,
80 saines) par distance de Mahalanobis dans l'espace (sin teinte, cos teinte,
saturation, luminosité, saturation × luminosité). Les autres gardes portent sur la
présence de matière colorée, le grain de coloration, les bords nets de l'objet et
la part de fond pâle. Banc d'essai de calibration : 316/320 cellules du corpus
acceptées, 76/78 contre-exemples (photos naturelles et recolorages adverses) refusés.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

TAILLE_ANALYSE = 96

# Ajustement hors ligne (scripts/calibration) du dôme de couleur Giemsa.
DOME_MOYENNE = np.array([-0.24503, 0.72654, 0.18504, 0.52223, 0.13608], dtype=np.float32)
DOME_INV_CHOL = np.array(
    [
        [2.3353, 0.0, 0.0, 0.0, 0.0],
        [-3.47637, 3.74007, 0.0, 0.0, 0.0],
        [0.58918, -0.55032, 7.03374, 0.0, 0.0],
        [0.22692, 0.82809, -10.1358, 5.24181, 0.0],
        [-0.32128, -1.27991, -20.33569, -4.92895, 40.30471],
    ],
    dtype=np.float32,
)
DOME_SEUIL = 4.0

SATURATION_P95_MIN = 0.02
GRAIN_MIN = 0.006
GRAIN_MAX = 0.050
ARETES_MIN = 0.03
MATIERE_MIN = 0.03
FOND_MAX = 0.92

MOTIF_PALETTE = "La palette de couleurs ne correspond pas à une coloration au Giemsa."
MOTIF_SATURATION = "L'image est trop peu colorée pour une lame au Giemsa."
MOTIF_LISSE = "La surface est trop lisse pour une cellule colorée."
MOTIF_DETAIL = "Le niveau de détail dépasse celui d'un recadrage microscopique."
MOTIF_BORDS = "Trop peu de structure nette : une cellule présente des bords de coloration marqués."
MOTIF_MATIERE = "Aucune matière dense comparable au cytoplasme ou à la chromatine."
MOTIF_VIDE = "L'image est presque entièrement un fond pâle, sans cellule exploitable."


@dataclass(frozen=True)
class VerdictValidite:
    """Résultat du contrôle de domaine : acceptation, motifs de refus, mesures."""

    accepte: bool
    motifs: tuple[str, ...]
    mesures: dict[str, float]


def _vecteurs(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    ang = h * 2.0 * np.pi
    return np.stack(
        [np.sin(ang).ravel(), np.cos(ang).ravel(), s.ravel(), v.ravel(), (s * v).ravel()],
        axis=1,
    )


def evaluer_validite(image: Image.Image) -> VerdictValidite:
    """Mesure la conformité de l'image au domaine des frottis Giemsa."""
    im = image.convert("RGB").resize((TAILLE_ANALYSE, TAILLE_ANALYSE), Image.BILINEAR)
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32) / 255.0
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    fond = (v > 0.72) & (s < 0.22)
    objet = ~fond

    mesures: dict[str, float] = {}
    motifs: list[str] = []

    distances = np.sqrt(
        ((DOME_INV_CHOL @ (_vecteurs(h, s, v) - DOME_MOYENNE).T).T ** 2).sum(axis=1)
    )
    mesures["dome"] = float((distances[objet.ravel()] < DOME_SEUIL).mean()) if objet.any() else 0.0
    if mesures["dome"] < 0.80:
        motifs.append(MOTIF_PALETTE)

    mesures["saturation"] = float(np.percentile(s[objet], 95)) if objet.any() else 0.0
    if mesures["saturation"] < SATURATION_P95_MIN:
        motifs.append(MOTIF_SATURATION)

    gradient = np.hypot(*np.gradient(v))
    mesures["grain"] = float(gradient.mean())
    mesures["aretes"] = float((gradient > 0.18).mean())
    if mesures["grain"] < GRAIN_MIN:
        motifs.append(MOTIF_LISSE)
    if mesures["grain"] > GRAIN_MAX:
        motifs.append(MOTIF_DETAIL)
    if mesures["aretes"] < ARETES_MIN:
        motifs.append(MOTIF_BORDS)

    mesures["matiere"] = float((v[objet] < 0.45).mean()) if objet.any() else 0.0
    if mesures["matiere"] < MATIERE_MIN:
        motifs.append(MOTIF_MATIERE)

    mesures["fond"] = float(fond.mean())
    if mesures["fond"] > FOND_MAX:
        motifs.append(MOTIF_VIDE)

    return VerdictValidite(not motifs, tuple(motifs), mesures)
