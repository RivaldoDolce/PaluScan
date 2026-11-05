"""Encapsulation de l'inférence ONNXRuntime utilisée par l'application web."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import onnxruntime as ort
from PIL import Image

from .config import CLASSES, IMG_SIZE, NORMALISATION, ONNX_PATH

_MEAN = np.array(NORMALISATION["mean"], dtype=np.float32).reshape(3, 1, 1)
_STD = np.array(NORMALISATION["std"], dtype=np.float32).reshape(3, 1, 1)


@dataclass(frozen=True)
class Prediction:
    """Résultat d'analyse d'une cellule."""

    label: int
    label_name: str
    prob_infected: float
    prob_healthy: float
    latency_ms: float


class Predictor:
    """Charge une session ONNXRuntime unique et sert les requêtes d'inférence."""

    def __init__(self, onnx_path=ONNX_PATH) -> None:
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        self.session = ort.InferenceSession(
            str(onnx_path), options, providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def preprocess(self, image: Image.Image) -> np.ndarray:
        """Redimensionne, normalise et met en forme l'image d'entrée."""
        rgb = image.convert("RGB").resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
        array = np.asarray(rgb, dtype=np.float32).transpose(2, 0, 1) / 255.0
        return ((array - _MEAN) / _STD)[np.newaxis, ...]

    def predict_array(self, tensor: np.ndarray) -> Prediction:
        """Inférence sur un tenseur déjà prétraité, format (1, 3, H, W)."""
        started = time.perf_counter()
        logits = self.session.run(None, {self.input_name: tensor.astype(np.float32)})[0][0]
        latency = (time.perf_counter() - started) * 1000
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        label = int(np.argmax(probs))
        return Prediction(
            label=label,
            label_name=CLASSES[label],
            prob_infected=float(probs[0]),
            prob_healthy=float(probs[1]),
            latency_ms=latency,
        )

    def predict_image(self, image: Image.Image) -> Prediction:
        """Inférence directe sur une image PIL fournie par l'utilisateur."""
        return self.predict_array(self.preprocess(image))
