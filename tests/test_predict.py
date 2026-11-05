"""Inférence ONNX et explicabilité par occlusion."""

import numpy as np
import pytest
from PIL import Image

from paluscan.config import CLASSES, IMG_SIZE
from paluscan.explain import OcclusionExplainer
from paluscan.predict import Predictor


@pytest.fixture(scope="module")
def predicteur():
    return Predictor()


def test_prediction_sur_image_synthetique(predicteur):
    image = Image.new("RGB", (120, 120), (180, 60, 80))
    p = predicteur.predict_image(image)
    assert p.label in (0, 1)
    assert p.label_name in CLASSES
    assert p.prob_infected + p.prob_healthy == pytest.approx(1.0, abs=1e-5)
    assert p.latency_ms >= 0.0


def test_preprocess_dimensions_et_normalisation(predicteur):
    image = Image.new("RGB", (100, 140), (128, 128, 128))
    tensor = predicteur.preprocess(image)
    assert tensor.shape == (1, 3, IMG_SIZE, IMG_SIZE)
    gris = tensor[0, 0]
    assert gris.max() <= 0.02
    assert gris.min() >= -0.02


def test_determinisme(predicteur):
    image = Image.new("RGB", (64, 64), (90, 30, 40))
    premier = predicteur.predict_image(image)
    second = predicteur.predict_image(image)
    assert premier.prob_infected == second.prob_infected


def test_carte_occlusion_bornee(predicteur):
    explainer = OcclusionExplainer(predicteur.session, predicteur.input_name, patch=8, stride=4)
    image = Image.new("RGB", (64, 64), (200, 70, 90))
    tensor = predicteur.preprocess(image)
    carte = explainer.heatmap(tensor, class_index=0)
    assert carte.shape == (IMG_SIZE, IMG_SIZE)
    assert carte.min() >= 0.0 and carte.max() <= 1.0


def test_superposition_overlay(predicteur):
    explainer = OcclusionExplainer(predicteur.session, predicteur.input_name)
    image = Image.new("RGB", (64, 64), (200, 70, 90))
    carte = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.float32)
    superposition = explainer.overlay(image, carte)
    assert superposition.size == (IMG_SIZE * 2, IMG_SIZE * 2)
