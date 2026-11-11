"""AuraSR-v2 (fal.ai, 2025): single-step generative GigaGAN upscaler."""

import json
from pathlib import Path

import torch
from PIL import Image

from .base import Upscaler

HF_REPO = "fal/AuraSR-v2"


class AuraSRUpscaler(Upscaler):
    id = "aurasr"
    name = "AuraSR-v2 (GigaGAN)"

    def load(self, device: torch.device) -> None:
        from aura_sr import AuraSR
        from huggingface_hub import snapshot_download
        from safetensors.torch import load_file

        super().load(device)
        repo_dir = Path(snapshot_download(HF_REPO))
        config = json.loads((repo_dir / "config.json").read_text())
        self.model = AuraSR(config, device=str(device))
        self.model.upsampler.load_state_dict(load_file(repo_dir / "model.safetensors"), strict=True)

    def upscale(self, image: Image.Image) -> Image.Image:
        # Overlapped tiling hides seams between the 64px tiles the model works on.
        return self.model.upscale_4x_overlapped(image)
