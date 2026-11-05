"""Export du réseau PyTorch vers ONNX pour une inférence de production légère.

Usage : uv run python scripts/export_onnx.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paluscan.config import ONNX_PATH, TORCH_PATH  # noqa: E402
from paluscan.model import MalariaNet  # noqa: E402


def main() -> None:
    checkpoint = torch.load(TORCH_PATH, weights_only=True)
    model = MalariaNet()
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    dummy = torch.randn(1, 3, 64, 64)
    ONNX_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        dummy,
        ONNX_PATH,
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )

    # Le moteur d'export externalise les poids ; on les réincorpore pour
    # obtenir un fichier unique, plus simple à versionner et à déployer.
    import onnx

    merged = onnx.load(ONNX_PATH, load_external_data=True)
    onnx.save_model(merged, ONNX_PATH, save_as_external_data=False)
    external = ONNX_PATH.with_suffix(".onnx.data")
    if external.exists():
        external.unlink()
    size_kb = ONNX_PATH.stat().st_size / 1024
    print(f"Modèle exporté : {ONNX_PATH} ({size_kb:.0f} Ko)")


if __name__ == "__main__":
    main()
