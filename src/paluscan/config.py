"""Chemins d'accès et constantes partagées du projet."""

from pathlib import Path

PROJECT_ROOT = Path(__import__("os").environ.get("PALUSCAN_ROOT", Path(__file__).resolve().parents[2]))

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "cell_images"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

ONNX_PATH = MODELS_DIR / "paluscan.onnx"
TORCH_PATH = MODELS_DIR / "malaria_net.pt"
METRICS_PATH = REPORTS_DIR / "metrics.json"
BASELINE_PATH = REPORTS_DIR / "baseline_preds.npz"

IMG_SIZE = 64
CLASSES = ("parasitized", "uninfected")
SEED = 42

NORMALISATION = {"mean": (0.5, 0.5, 0.5), "std": (0.5, 0.5, 0.5)}
