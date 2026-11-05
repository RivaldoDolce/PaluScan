"""Architecture CNN compacte, dimensionnée pour une inférence CPU fluide.

Quatre blocs convolutif-pooling puis une tête dense : environ 178 000 paramètres,
suffisants pour la morphologie des cellules infectées tout en restant léger à
servir (poids ONNX de l'ordre du mégaoctet).
"""

from __future__ import annotations

import torch
import torch.nn as nn


class ConvBlock(nn.Sequential):
    """Convolution 3x3, normalisation, ReLU puis sous-échantillonnage par 2."""

    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )


class MalariaNet(nn.Module):
    """Classifieur binaire cellule parasitée / cellule saine."""

    def __init__(self, n_classes: int = 2) -> None:
        super().__init__()
        self.features = nn.Sequential(
            ConvBlock(3, 16),  # 64 -> 32
            ConvBlock(16, 32),  # 32 -> 16
            ConvBlock(32, 48),  # 16 -> 8
            ConvBlock(48, 64),  # 8 -> 4
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, n_classes),
        )
        self._init_weights()

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Extraction de caractéristiques puis classification."""
        return self.classifier(self.features(x))
