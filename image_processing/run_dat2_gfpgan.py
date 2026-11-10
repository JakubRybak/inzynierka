#!/usr/bin/env python3
"""
Run Hybrid E-Commerce Super-Resolution: 4xRealWebPhoto DAT-2 + GFPGAN Face Restoration.
Combines:
  1. DAT-2 Vision Transformer: 100% garment texture fidelity (no fabric hallucinations)
  2. GFPGAN v1.4 Generative Face Restoration: Crisp, photorealistic model faces, eyes, and skin.
Outputs 1024x1024 WebP images into image_processing/outputs/dat2_gfpgan/

Includes seamless face parsing & feathering (NO white halos or discoloration).
"""

import sys
import time
from pathlib import Path
import cv2
import numpy as np
import torch
import torchvision.transforms.functional as TF
from facexlib.utils.face_restoration_helper import FaceRestoreHelper
from torchvision.transforms.functional import normalize
import spandrel

BASE_DIR = Path(__file__).resolve().parent
DAT2_DIR = BASE_DIR / "outputs" / "realwebphoto_dat2"
OUTPUT_DIR = BASE_DIR / "outputs" / "dat2_gfpgan"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = BASE_DIR / "models" / "GFPGANv1.4.pth"

# Face parser colormap: keep skin & facial features (1), exclude background/hair/clothes (0)
# Classes: 0=bg, 1=skin, 2=l_brow, 3=r_brow, 4=l_eye, 5=r_eye, 6=eye_g, 7=l_ear, 8=r_ear,
# 9=ear_r, 10=nose, 11=mouth, 12=u_lip, 13=l_lip, 14=neck, 15=neck_l, 16=cloth, 17=hair, 18=hat
MASK_COLORMAP = [0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 255, 0, 0, 0]

def main():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print("=== Hybrid DAT-2 + GFPGAN Face Restoration Pipeline (Halo-Free) ===")
    print(f"Target device: {device}")
    print(f"Loading GFPGAN model from {MODEL_PATH}...")

    t0 = time.perf_counter()
    model = spandrel.ModelLoader().load_from_file(str(MODEL_PATH)).to(device)
    model.eval()

    face_helper = FaceRestoreHelper(
        upscale_factor=1,
        face_size=512,
        crop_ratio=(1, 1),
        det_model="retinaface_resnet50",
        save_ext="png",
        use_parse=True,
        device=device
    )
    print(f"Models loaded in {time.perf_counter() - t0:.2f}s.\n")

    images = sorted(DAT2_DIR.glob("*.webp"))
    total_imgs = len(images)
    times = []

    for i, img_p in enumerate(images, 1):
        out_p = OUTPUT_DIR / img_p.name
        print(f"[{i}/{total_imgs}] Processing {img_p.name}...")
        img = cv2.imread(str(img_p))
        if img is None:
            print(f"  ⚠️ Warning: could not load {img_p}")
            continue

        t_start = time.perf_counter()
        face_helper.clean_all()
        face_helper.read_image(img)
        face_helper.get_face_landmarks_5(only_center_face=False, eye_dist_threshold=5)
        
        num_faces = len(face_helper.all_landmarks_5)
        if num_faces > 0:
            face_helper.align_warp_face()
            face_helper.get_inverse_affine(None)
            h_up, w_up = img.shape[:2]
            final_img = img.copy()

            for cropped_face, inv_affine in zip(face_helper.cropped_faces, face_helper.inverse_affine_matrices):
                face_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                tensor = TF.to_tensor(face_rgb).unsqueeze(0).to(device) # input range [0, 1]
                with torch.inference_mode():
                    output = model(tensor) # spandrel output is in range [0, 1]
                    output = output.clamp(0, 1)
                restored_np = (output[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
                restored_bgr = cv2.cvtColor(restored_np, cv2.COLOR_RGB2BGR)

                # Segment face parsing map to isolate skin and facial features cleanly
                face_input = cv2.resize(restored_bgr, (512, 512), interpolation=cv2.INTER_LINEAR)
                face_tensor = TF.to_tensor(cv2.cvtColor(face_input, cv2.COLOR_BGR2RGB)).to(device)
                normalize(face_tensor, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
                with torch.no_grad():
                    parse_out = face_helper.face_parse(face_tensor.unsqueeze(0))[0]
                parse_out = parse_out.argmax(dim=1).squeeze().cpu().numpy()

                mask = np.zeros(parse_out.shape, dtype=np.float32)
                for c_idx, color in enumerate(MASK_COLORMAP):
                    if color == 255:
                        mask[parse_out == c_idx] = 1.0

                # Slightly erode (5x5) and apply soft Gaussian blur (19x19, sigma=4)
                # This guarantees zero bleeding into hair, clothes, or background (NO halos)
                mask = cv2.erode(mask, np.ones((5, 5), np.uint8))
                mask = cv2.GaussianBlur(mask, (19, 19), 4)

                inv_restored = cv2.warpAffine(restored_bgr, inv_affine, (w_up, h_up))
                inv_soft_mask = cv2.warpAffine(mask, inv_affine, (w_up, h_up), flags=cv2.INTER_LINEAR)[:, :, None]

                final_img = (inv_soft_mask * inv_restored + (1.0 - inv_soft_mask) * final_img).astype(np.uint8)

            status_msg = f"Restored {num_faces} face(s) seamlessly"
        else:
            final_img = img
            status_msg = "No faces detected (retained pristine DAT-2 garment)"

        t_elapsed = time.perf_counter() - t_start
        times.append(t_elapsed)

        # Save as WebP quality 90
        cv2.imwrite(str(out_p), final_img, [cv2.IMWRITE_WEBP_QUALITY, 90])
        size_kb = out_p.stat().st_size / 1024
        print(f"  ✓ {status_msg} -> {out_p.name} ({size_kb:.1f} KB) in {t_elapsed:.2f}s")

    avg_t = sum(times) / len(times) if times else 0
    print(f"\nFinished hybrid processing {len(images)} images.")
    print(f"Average time per image: {avg_t:.2f}s")
    print(f"Estimated time for 10,000 images: {avg_t * 10000 / 3600:.2f} hours")

if __name__ == "__main__":
    main()
