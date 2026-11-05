"""Dataset PyTorch et augmentations légères, sans dépendance à torchvision."""

from __future__ import annotations

import random
from typing import Callable

import numpy as np
from PIL import Image
from torch.utils.data import Dataset

from .config import IMG_SIZE, NORMALISATION
from .data import CellRecord

_ROTATIONS = (None, Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270)
_MEAN = np.array(NORMALISATION["mean"], dtype=np.float32).reshape(3, 1, 1)
_STD = np.array(NORMALISATION["std"], dtype=np.float32).reshape(3, 1, 1)


def load_tensor(record: CellRecord, size: int = IMG_SIZE) -> np.ndarray:
    """Charge une image, la redimensionne et la normalise en tenseur CHW."""
    with Image.open(record.path) as img:
        rgb = img.convert("RGB").resize((size, size), Image.BILINEAR)
    array = np.asarray(rgb, dtype=np.float32).transpose(2, 0, 1) / 255.0
    return (array - _MEAN) / _STD


def augment(tensor: np.ndarray, rng: random.Random) -> np.ndarray:
    """Retournements et rotations à angles droits, invariants morphologiques ici."""
    if rng.random() < 0.5:
        tensor = tensor[:, :, ::-1]
    if rng.random() < 0.5:
        tensor = tensor[:, ::-1, :]
    rotation = rng.choice(_ROTATIONS)
    if rotation is not None:
        tensor = np.rot90(tensor, k=_ROTATIONS.index(rotation), axes=(1, 2))
    return np.ascontiguousarray(tensor)


class MalariaDataset(Dataset):
    """Collection de cellules avec augmentation appliquée côté entraînement."""

    def __init__(
        self,
        records: list[CellRecord],
        train: bool = False,
        size: int = IMG_SIZE,
        seed: int = 0,
    ) -> None:
        self.records = records
        self.train = train
        self.size = size
        self._rng = random.Random(seed)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> tuple[np.ndarray, int]:
        record = self.records[index]
        tensor = load_tensor(record, self.size)
        if self.train:
            tensor = augment(tensor, self._rng)
        return tensor, record.label
