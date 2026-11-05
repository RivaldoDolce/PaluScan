"""Cartes d'importance par sensibilité à l'occlusion, via ONNXRuntime.

Principe : on masque successivement des fenêtres de l'image et on mesure la
chute du logit de la classe prédite. Les régions dont le masquage détruit la
confiance portent l'information discriminante. La méthode n'exige aucun
gradient, ce qui la rend compatible avec un moteur d'inférence seul.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from .config import IMG_SIZE


class OcclusionExplainer:
    """Produit une carte de chaleur normalisée pour une image déjà prétraitée."""

    def __init__(self, session, input_name: str, patch: int = 8, stride: int = 4) -> None:
        self.session = session
        self.input_name = input_name
        self.patch = patch
        self.stride = stride

    def heatmap(self, tensor: np.ndarray, class_index: int) -> np.ndarray:
        """Renvoie une carte (IMG_SIZE, IMG_SIZE) dans [0, 1].

        tensor : tenseur normalisé (1, 3, H, W).
        """
        baseline = float(self.session.run(None, {self.input_name: tensor})[0][0, class_index])
        _, _, h, w = tensor.shape

        acc = np.zeros((h, w), dtype=np.float32)
        weight = np.zeros((h, w), dtype=np.float32)
        mask = np.ones_like(tensor, dtype=np.float32)
        fill = tensor.mean()

        for top in range(0, h - self.patch + 1, self.stride):
            for left in range(0, w - self.patch + 1, self.stride):
                occluded = tensor.copy()
                occluded[:, :, top : top + self.patch, left : left + self.patch] = fill
                logit = float(
                    self.session.run(None, {self.input_name: occluded.astype(np.float32)})[0][0, class_index]
                )
                acc[top : top + self.patch, left : left + self.patch] += baseline - logit
                weight[top : top + self.patch, left : left + self.patch] += 1.0

        acc /= np.maximum(weight, 1.0)
        acc = np.maximum(acc, 0.0)
        if acc.max() > 0:
            acc /= acc.max()
        return acc

    @staticmethod
    def overlay(image: Image.Image, map_array: np.ndarray, alpha: float = 0.45) -> Image.Image:
        """Superpose la carte de chaleur à l'image d'origine (échelle 150 px)."""
        base = image.convert("RGB").resize((IMG_SIZE * 2, IMG_SIZE * 2), Image.BILINEAR)
        resized = Image.fromarray((map_array * 255).astype(np.uint8)).resize(base.size, Image.BILINEAR)
        heat = np.asarray(resized, dtype=np.float32) / 255.0

        # Dégradé rouge-jaune lisible sur fond de frottis.
        r = np.clip(heat * 1.6, 0, 1)
        g = np.clip(heat * heat * 0.9, 0, 1)
        b = np.clip(heat * heat * 0.2, 0, 1)
        tint = np.stack([r, g, b], axis=-1)

        canvas = np.asarray(base, dtype=np.float32) / 255.0
        weight = alpha * heat[..., None]
        blended = canvas * (1 - weight) + tint * weight
        return Image.fromarray((np.clip(blended, 0, 1) * 255).astype(np.uint8))
