"""Hybrid e-commerce upscaler: DAT-2 for the garment + GFPGAN for the model's face.

Pipeline:
    1. DAT-2 upscales the whole photo 4x.
    2. RetinaFace finds faces; each one is aligned to a 512x512 crop.
    3. GFPGAN v1.4 restores the crop (eyes, lips, skin).
    4. ParseNet face parsing builds a mask of skin + facial features only
       (background, hair and clothes excluded), slightly eroded and feathered.
    5. The restored face is warped back and alpha-blended into the DAT-2 image.
Photos without a detectable face are returned exactly as DAT-2 produced them.
"""

from pathlib import Path

import cv2
import numpy as np
import torch
import torchvision.transforms.functional as TF
from PIL import Image

from .weights import DAT2_WEIGHTS, GFPGAN_WEIGHTS, get_checkpoint

FACE_CROP_SIZE = 512

# ParseNet classes kept in the blend mask (1) vs. excluded (0):
# 0 bg, 1 skin, 2-3 brows, 4-5 eyes, 6 glasses, 7-9 ears, 10 nose, 11 mouth, 12-13 lips,
# 14 neck, 15 necklace, 16 cloth, 17 hair, 18 hat
FACE_MASK_CLASSES = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0]

# Erode and blur the mask before blending the restored crop.
MASK_ERODE_KERNEL = np.ones((5, 5), np.uint8)
MASK_BLUR_KERNEL = (19, 19)
MASK_BLUR_SIGMA = 4


class FaceRestorer:
    """Detects faces in a BGR image and replaces them with GFPGAN-restored versions."""

    def __init__(self, device: torch.device, weights_dir: Path) -> None:
        import spandrel
        from facexlib.utils.face_restoration_helper import FaceRestoreHelper

        self.device = device
        model_path = get_checkpoint(weights_dir, GFPGAN_WEIGHTS)
        self.gfpgan = spandrel.ModelLoader().load_from_file(str(model_path)).to(device).eval()
        self.helper = FaceRestoreHelper(
            upscale_factor=1,
            face_size=FACE_CROP_SIZE,
            crop_ratio=(1, 1),
            det_model="retinaface_resnet50",
            save_ext="png",
            use_parse=True,
            device=str(device),
        )

    def restore(self, image_bgr: np.ndarray) -> np.ndarray:
        self.helper.clean_all()
        self.helper.read_image(image_bgr)
        self.helper.get_face_landmarks_5(only_center_face=False, eye_dist_threshold=5)
        if not self.helper.all_landmarks_5:
            return image_bgr

        self.helper.align_warp_face()
        self.helper.get_inverse_affine(None)

        height, width = image_bgr.shape[:2]
        result = image_bgr.astype(np.float32)
        for face_crop, inverse_affine in zip(self.helper.cropped_faces, self.helper.inverse_affine_matrices):
            restored_face = self._restore_face(face_crop)
            mask = self._face_mask(restored_face)

            face_in_image = cv2.warpAffine(restored_face, inverse_affine, (width, height))
            mask_in_image = cv2.warpAffine(mask, inverse_affine, (width, height), flags=cv2.INTER_LINEAR)[:, :, None]
            result = mask_in_image * face_in_image + (1.0 - mask_in_image) * result

        return result.astype(np.uint8)

    def _restore_face(self, face_bgr: np.ndarray) -> np.ndarray:
        """Run GFPGAN on an aligned 512x512 face crop. Spandrel works in [0, 1] RGB."""
        tensor = TF.to_tensor(cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            output = self.gfpgan(tensor).clamp(0, 1)
        restored_rgb = (output[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        return cv2.cvtColor(restored_rgb, cv2.COLOR_RGB2BGR)

    def _face_mask(self, face_bgr: np.ndarray) -> np.ndarray:
        """Soft float mask (0..1) covering skin and facial features of a 512x512 face crop."""
        face_rgb = cv2.cvtColor(cv2.resize(face_bgr, (FACE_CROP_SIZE, FACE_CROP_SIZE)), cv2.COLOR_BGR2RGB)
        tensor = TF.normalize(TF.to_tensor(face_rgb), (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)).to(self.device)
        with torch.inference_mode():
            parsing = self.helper.face_parse(tensor.unsqueeze(0))[0]
        labels = parsing.argmax(dim=1).squeeze().cpu().numpy()

        mask = np.isin(labels, np.flatnonzero(FACE_MASK_CLASSES)).astype(np.float32)
        mask = cv2.erode(mask, MASK_ERODE_KERNEL)
        return cv2.GaussianBlur(mask, MASK_BLUR_KERNEL, MASK_BLUR_SIGMA)


class Dat2Gfpgan:
    """Load DAT-2 and GFPGAN once and reuse them across product photos."""

    def __init__(self, device: torch.device, weights_dir: Path) -> None:
        from spandrel import ModelLoader

        self.device = device
        self.dat2 = ModelLoader().load_from_file(str(get_checkpoint(weights_dir, DAT2_WEIGHTS))).to(device).eval()
        self.faces = FaceRestorer(device, weights_dir)

    def upscale(self, image: Image.Image) -> Image.Image:
        tensor = TF.to_tensor(image).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            output = self.dat2(tensor).squeeze(0).clamp(0, 1)
        upscaled = TF.to_pil_image(output.cpu())
        image_bgr = cv2.cvtColor(np.asarray(upscaled), cv2.COLOR_RGB2BGR)
        restored_bgr = self.faces.restore(image_bgr)
        return Image.fromarray(cv2.cvtColor(restored_bgr, cv2.COLOR_BGR2RGB))
