"""Classical baseline: Lanczos resampling followed by an unsharp mask (no neural network)."""

from PIL import Image, ImageFilter

from .base import Upscaler

SCALE = 4


class LanczosUpscaler(Upscaler):
    id = "lanczos"
    name = "Lanczos + Unsharp Mask"

    def warmup(self, sample: Image.Image) -> None:
        pass

    def upscale(self, image: Image.Image) -> Image.Image:
        upscaled = image.resize((image.width * SCALE, image.height * SCALE), Image.Resampling.LANCZOS)
        return upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
