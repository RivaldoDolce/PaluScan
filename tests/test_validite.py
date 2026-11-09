"""Garde-fou d'entrée : acceptation des frottis, refus des images hors domaine."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from paluscan.validite import evaluer_validite

REPERTOIRE_EXEMPLES = Path(__file__).resolve().parents[1] / "src/paluscan/app/static/img/exemples"


def cellule_giemsa(germe: int = 3, taille: int = 96) -> Image.Image:
    """Cellule synthétique conforme au domaine : fond pâle, cytoplasme corail, chromatine violette."""
    rng = np.random.default_rng(germe)
    image = Image.new("RGB", (taille, taille), (222, 204, 213))
    dessin = ImageDraw.Draw(image)
    centre = taille / 2
    rayon = taille * 0.375
    dessin.ellipse(
        [centre - rayon, centre - rayon, centre + rayon, centre + rayon],
        fill=(190, 126, 156),
        outline=(140, 80, 110),
        width=3,
    )
    for _ in range(8):
        x = centre + rng.uniform(-rayon / 2.4, rayon / 2.4)
        y = centre + rng.uniform(-rayon / 2.4, rayon / 2.4)
        r = rng.uniform(2.5, 5)
        dessin.ellipse([x - r, y - r, x + r, y + r], fill=(88, 54, 112))
    tableau = np.asarray(image, dtype=np.float32)
    grain = rng.normal(0, 6, tableau.shape[:2])[..., None]
    tableau = np.clip(tableau + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(tableau)


def _vers_png(image: Image.Image) -> Image.Image:
    tampon = __import__("io").BytesIO()
    image.save(tampon, format="PNG")
    tampon.seek(0)
    return Image.open(tampon)


def test_cellules_reelles_du_corpus_sont_acceptees():
    chemins = sorted(REPERTOIRE_EXEMPLES.glob("*.png"))
    assert len(chemins) == 12
    refus = [chemin.name for chemin in chemins if not evaluer_validite(Image.open(chemin)).accepte]
    assert refus == []


def test_cellule_synthetique_acceptee():
    verdict = evaluer_validite(_vers_png(cellule_giemsa()))
    assert verdict.accepte, verdict.motifs


def test_aplat_gris_refuse():
    verdict = evaluer_validite(Image.new("RGB", (96, 96), (128, 128, 128)))
    assert not verdict.accepte


def test_gradient_vert_bleu_refuse():
    grad = np.linspace(0, 1, 96)[None, :, None] * np.array([40, 180, 120])[None, None, :]
    image = Image.fromarray(np.tile(grad, (96, 1, 1)).astype(np.uint8))
    verdict = evaluer_validite(image)
    assert not verdict.accepte
    assert any("Giemsa" in motif for motif in verdict.motifs)


def test_photo_bruit_refusee():
    rng = np.random.default_rng(5)
    bruit = rng.integers(0, 255, (96, 96, 3), dtype=np.uint8)
    verdict = evaluer_validite(Image.fromarray(bruit))
    assert not verdict.accepte


def test_document_blanc_refuse():
    image = Image.new("RGB", (96, 96), (250, 250, 250))
    dessin = ImageDraw.Draw(image)
    for y in range(10, 90, 8):
        dessin.line([(8, y), (88, y)], fill=(40, 40, 60), width=2)
    verdict = evaluer_validite(image)
    assert not verdict.accepte


def test_grayscale_refuse():
    rng = np.random.default_rng(8)
    gris = rng.integers(60, 200, (96, 96), dtype=np.uint8)
    verdict = evaluer_validite(Image.fromarray(np.stack([gris] * 3, axis=2)))
    assert not verdict.accepte


def test_motifs_renseignes_et_mesures_completes():
    verdict = evaluer_validite(Image.new("RGB", (96, 96), (200, 200, 200)))
    assert verdict.motifs
    assert {"dome", "saturation", "grain", "aretes", "matiere", "fond"} <= set(verdict.mesures)


@pytest.mark.skipif(
    not (Path("/tmp/corpus-echantillon").is_dir()),
    reason="échantillon de calibration absent de cette machine",
)
def test_echantillon_corpus_majoritairement_accepte():
    positifs = sorted(Path("/tmp/corpus-echantillon").glob("*/*.png"))
    acceptes = sum(evaluer_validite(Image.open(p)).accepte for p in positifs)
    assert acceptes / len(positifs) >= 0.95
