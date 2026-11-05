"""Préparation des données : décompression, vérification et exemples de démonstration.

Usage : uv run python scripts/prepare_data.py [--archive /tmp/cell_images.zip]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paluscan.config import CLASSES, RAW_DIR  # noqa: E402
from paluscan.data import discover, grouped_split  # noqa: E402


def extract(archive: Path) -> None:
    """Décompresse l'archive NIH dans data/cell_images si nécessaire."""
    if (RAW_DIR / "Parasitized").is_dir():
        print(f"Jeu déjà extrait : {RAW_DIR}")
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(RAW_DIR)
    # L'archive contient parfois un dossier racine cell_images/.
    nested = RAW_DIR / "cell_images"
    if nested.is_dir():
        for item in nested.iterdir():
            shutil.move(str(item), RAW_DIR / item.name)
        nested.rmdir()
    print(f"Extraction terminée dans {RAW_DIR}")


def audit() -> dict:
    """Compte les cellules, lames et vérifie la cohérence des classes."""
    records = discover(RAW_DIR)
    train, val, test = grouped_split(records)
    report = {
        "total": len(records),
        "par_classe": {name: sum(r.label == i for r in records) for i, name in enumerate(CLASSES)},
        "lames": len({r.slide for r in records}),
        "lots": {
            "entrainement": {"cellules": len(train), "lames": len({r.slide for r in train})},
            "validation": {"cellules": len(val), "lames": len({r.slide for r in val})},
            "test": {"cellules": len(test), "lames": len({r.slide for r in test})},
        },
    }
    sizes = {Image.open(r.path).size for r in records[:2000]}
    report["dimensions_rencontrées"] = sorted({f"{w}x{h}" for w, h in sizes})
    return report


def export_examples(count_per_class: int = 6) -> None:
    """Copie quelques cellules du lot de test comme exemples d'analyse."""
    _, _, test = grouped_split(discover(RAW_DIR))
    rng = np.random.default_rng(7)
    examples = ROOT / "src" / "paluscan" / "app" / "static" / "img" / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    chosen: list[tuple[str, Path]] = []
    for label, name in enumerate(CLASSES):
        pool = [r for r in test if r.label == label]
        idx = rng.choice(len(pool), size=min(count_per_class, len(pool)), replace=False)
        for i in idx:
            chosen.append((name, pool[int(i)].path))
    for name, path in chosen:
        target = examples / f"{name[:4]}_{path.name}"
        shutil.copy(path, target)
    print(f"{len(chosen)} exemples copiés dans {examples}")


def main() -> None:
    """Extrait, audite et prépare le jeu NIH : découpage par lame et échantillon de démonstration."""
    parser = argparse.ArgumentParser(description="Préparation du jeu NIH malaria")
    parser.add_argument("--archive", type=Path, default=Path("/tmp/cell_images.zip"))
    args = parser.parse_args()

    if not args.archive.exists():
        raise SystemExit(f"Archive introuvable : {args.archive} (voir data/README.md)")
    extract(args.archive)
    report = audit()
    (ROOT / "reports" / "dataset_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    export_examples()


if __name__ == "__main__":
    main()
