"""Foreground masking with ZhengPeng7/BiRefNet_lite-matting.

Tested with Hugging Face revision 99c33412e3f58e1f33187abdc8c435c645243690.
Pass a local snapshot containing the weights, config and model Python files.
The architecture requires timm, kornia and einops alongside PyTorch,
torchvision and transformers. Use a trusted snapshot because loading it
executes the included architecture code.
"""

import torch
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

PREPROCESS = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def load_model(weights, device="cpu"):
    """Load the local checkpoint and its custom architecture."""
    if device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("PyTorch MPS is unavailable in this environment")
    return AutoModelForImageSegmentation.from_pretrained(
        str(weights), trust_remote_code=True, local_files_only=True
    ).float().to(device).eval()


@torch.inference_mode()
def predict_mask(model, image):
    tensor = PREPROCESS(image).unsqueeze(0).to(next(model.parameters()).device)
    alpha = model(tensor)[-1].sigmoid()[0, 0]
    mask = transforms.functional.to_pil_image(alpha.cpu())
    return mask.resize(image.size, Image.Resampling.BILINEAR)
