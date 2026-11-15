"""Common interface implemented by every upscaling method."""

from abc import ABC, abstractmethod

import torch
from PIL import Image


class Upscaler(ABC):
    """A 4x image upscaler. Call `load()` once, then `upscale()` per image."""

    id: str
    name: str

    def load(self, device: torch.device) -> None:
        """Load model weights onto `device`. No-op for non-neural methods."""
        self.device = device

    def warmup(self, sample: Image.Image) -> None:
        """Run one throwaway inference so kernel compilation is not counted in timings."""
        self.upscale(sample)

    @abstractmethod
    def upscale(self, image: Image.Image) -> Image.Image:
        """Return `image` upscaled 4x (RGB in, RGB out)."""
