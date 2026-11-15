"""Stable Diffusion x4 Upscaler (Stability AI): text-guided latent diffusion."""

import torch
from PIL import Image

from ..device import empty_cache
from .base import Upscaler

HF_REPO = "stabilityai/stable-diffusion-x4-upscaler"
PROMPT = "high quality studio fashion catalog product photo, sharp fabric texture"
NEGATIVE_PROMPT = "blurry, low quality, distorted, artifacts, noisy"
INFERENCE_STEPS = 12
GUIDANCE_SCALE = 6.0


class StableDiffusionUpscaler(Upscaler):
    id = "sd_x4"
    name = "Stable Diffusion x4 Upscaler"

    def load(self, device: torch.device) -> None:
        from diffusers import StableDiffusionUpscalePipeline

        super().load(device)
        self.pipeline = StableDiffusionUpscalePipeline.from_pretrained(HF_REPO, torch_dtype=torch.float16).to(device)
        # Slicing + tiling keep decoding a 1024x1024 latent within Apple Silicon memory limits.
        self.pipeline.enable_attention_slicing()
        self.pipeline.vae.enable_slicing()
        self.pipeline.vae.enable_tiling()

    def warmup(self, sample: Image.Image) -> None:
        pass  # a full diffusion pass takes ~25 s; not worth it just for warmup

    def upscale(self, image: Image.Image) -> Image.Image:
        with torch.inference_mode():
            result = self.pipeline(
                prompt=PROMPT,
                negative_prompt=NEGATIVE_PROMPT,
                image=image,
                num_inference_steps=INFERENCE_STEPS,
                guidance_scale=GUIDANCE_SCALE,
            ).images[0]
        empty_cache(self.device)
        return result
