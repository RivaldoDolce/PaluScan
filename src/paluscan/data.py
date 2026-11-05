"""Ingestion des images et découpage par lame pour prévenir toute fuite de données.

Le jeu NIH provient de lames fines photographiées cellule par cellule : plusieurs
images successives proviennent de la même lame. Un découpage aléatoire mettrait
des cellules quasi identiques en entraînement et en test et gonflerait
artificiellement les performances. Toutes les cellules d'une même lame sont donc
affectées au même lot.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path

from .config import CLASSES, SEED

_SLIDE_RE = re.compile(r"^(?P<slide>.+)_cell_\d+$")


@dataclass(frozen=True)
class CellRecord:
    """Une cellule annotée et la lame dont elle provient."""

    path: Path
    label: int  # 0 = parasitée, 1 = saine
    slide: str


def slide_id(stem: str) -> str:
    """Extrait l'identifiant de lame d'un nom de fichier NIH."""
    match = _SLIDE_RE.match(stem)
    return match.group("slide") if match else stem


def discover(root: Path) -> list[CellRecord]:
    """Indexe les images des deux classes en résolvant la lame d'origine."""
    records: list[CellRecord] = []
    for label, name in enumerate(CLASSES):
        folder = root / name.capitalize()
        if not folder.is_dir():
            raise FileNotFoundError(f"Dossier de classe manquant : {folder}")
        for path in sorted(folder.glob("*.png")):
            records.append(CellRecord(path=path, label=label, slide=slide_id(path.stem)))
    return records


def grouped_split(
    records: list[CellRecord],
    train_frac: float = 0.70,
    val_frac: float = 0.15,
    seed: int = SEED,
) -> tuple[list[CellRecord], list[CellRecord], list[CellRecord]]:
    """Découpe en trois lots en répartissant les lames, pas les cellules."""
    rng = random.Random(seed)
    slides = sorted({record.slide for record in records})
    rng.shuffle(slides)

    n_train = int(len(slides) * train_frac)
    n_val = int(len(slides) * val_frac)
    train_slides = set(slides[:n_train])
    val_slides = set(slides[n_train : n_train + n_val])

    train: list[CellRecord] = []
    val: list[CellRecord] = []
    test: list[CellRecord] = []
    for record in records:
        if record.slide in train_slides:
            train.append(record)
        elif record.slide in val_slides:
            val.append(record)
        else:
            test.append(record)
    return train, val, test
