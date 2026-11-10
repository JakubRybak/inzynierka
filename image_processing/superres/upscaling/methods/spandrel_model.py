"""Single-pass neural upscalers loaded from .pth files via spandrel.

Used for Real-ESRGAN x4plus, 4x-UltraSharp (both RRDBNet CNNs) and 4xRealWebPhoto DAT-2 (transformer).
"""

import torch
from PIL import Image
from torchvision.transforms.functional import to_pil_image, to_tensor

from ..weights import WeightsFile
from .base import Upscaler


class SpandrelUpscaler(Upscaler):
    def __init__(self, method_id: str, name: str, weights: WeightsFile):
        self.id = method_id
        self.name = name
        self.weights = weights

    def load(self, device: torch.device) -> None:
        from spandrel import ModelLoader

        super().load(device)
        model_path = self.weights.ensure_downloaded()
        self.model = ModelLoader().load_from_file(str(model_path)).to(device).eval()

    def upscale(self, image: Image.Image) -> Image.Image:
        tensor = to_tensor(image).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            output = self.model(tensor).squeeze(0).clamp(0, 1)
        return to_pil_image(output.cpu())
