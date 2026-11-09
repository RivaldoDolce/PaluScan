"""Ressources applicatives partagées : moteur d'inférence, explicabilité, validation."""

from __future__ import annotations

import base64
import io
import json

import numpy as np
from PIL import Image, UnidentifiedImageError

from ..config import METRICS_PATH
from ..explain import OcclusionExplainer
from ..predict import Predictor
from ..validite import VerdictValidite, evaluer_validite

TAILLE_MAX_OCTETS = 8 * 1024 * 1024
FORMATS_ACCEPTES = {"PNG", "JPEG"}
NOMBRE_MAX_IMAGES_LOT = 12

_VALEURS_PAR_DEFAUT = {
    "seuil_youden": 0.5,
    "sensibilite": {"valeur": 0.9677},
    "specificite": {"valeur": 0.9541},
}


class ErreurValidation(Exception):
    """Requête client invalide : format, taille ou contenu d'image."""


class ErreurHorsDomaine(ErreurValidation):
    """Image décodable mais rejetée par le garde-fou de domaine."""

    def __init__(self, verdict: VerdictValidite) -> None:
        super().__init__("Cette image ne ressemble pas à un frottis sanguin coloré au Giemsa.")
        self.motifs = verdict.motifs


def charger_metriques() -> dict:
    """Lit reports/metrics.json ; repli sur des constantes validées si absent."""
    try:
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _VALEURS_PAR_DEFAUT


class Moteur:
    """Dépendances applicatives figées : session ONNX, explicateur, seuils."""

    def __init__(self, metriques: dict | None = None) -> None:
        self.predictor = Predictor()
        self.explainer = OcclusionExplainer(self.predictor.session, self.predictor.input_name)
        self.metriques = metriques if metriques is not None else charger_metriques()
        self.seuil_youden = float(self.metriques.get("seuil_youden", 0.5))
        self.sensibilite = float(self.metriques.get("sensibilite", {}).get("valeur", 0.9677))
        self.specificite = float(self.metriques.get("specificite", {}).get("valeur", 0.9541))

    def decodage(self, contenu: bytes) -> Image.Image:
        """Vérifie et décode un fichier image transmis par le client."""
        if len(contenu) > TAILLE_MAX_OCTETS:
            raise ErreurValidation("Image trop volumineuse (8 Mo maximum).")
        if not contenu:
            raise ErreurValidation("Fichier vide.")
        try:
            image = Image.open(io.BytesIO(contenu))
            image.load()
        except (UnidentifiedImageError, OSError) as exc:
            raise ErreurValidation("Format non pris en charge (PNG ou JPEG attendu).") from exc
        if image.format not in FORMATS_ACCEPTES:
            raise ErreurValidation("Format non pris en charge (PNG ou JPEG attendu).")
        return image.convert("RGB")

    def analyser(self, image: Image.Image, avec_carte: bool = False) -> dict:
        """Contrôle de domaine, puis inférence : décision au seuil de Youden + carte."""
        verdict = evaluer_validite(image)
        if not verdict.accepte:
            raise ErreurHorsDomaine(verdict)
        tensor = self.predictor.preprocess(image)
        p = self.predictor.predict_array(tensor)
        infectee = p.prob_infected >= self.seuil_youden
        resultat = {
            "infectee": infectee,
            "probabilite_infection": round(p.prob_infected, 4),
            "probabilite_sain": round(p.prob_healthy, 4),
            "latence_ms": round(p.latency_ms, 2),
            "seuil_youden": round(self.seuil_youden, 4),
        }
        if avec_carte:
            carte = self.explainer.heatmap(tensor, class_index=0)
            resultat["carte"] = self._carte_png(image, carte)
        return resultat

    def _carte_png(self, image: Image.Image, carte: np.ndarray) -> str:
        """Sérialise la superposition occlusion en PNG encodé base64."""
        superposition = self.explainer.overlay(image, carte)
        tampon = io.BytesIO()
        superposition.save(tampon, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(tampon.getvalue()).decode()


_moteur: Moteur | None = None


def get_moteur() -> Moteur:
    """Initialisation paresseuse unique, à l'appel de la première requête."""
    global _moteur
    if _moteur is None:
        _moteur = Moteur()
    return _moteur
