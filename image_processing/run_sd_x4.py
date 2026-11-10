#!/usr/bin/env python3
"""
Run Stable Diffusion x4 Upscaler on all sample images.
Uses official stabilityai/stable-diffusion-x4-upscaler on Apple Silicon (MPS).
Outputs 1024x1024 WebP images into image_processing/outputs/sd_x4/
"""

import sys
import time
from pathlib import Path
from PIL import Image
import torch

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "sample_images"
OUTPUT_DIR = BASE_DIR / "outputs" / "sd_x4"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = "high quality studio fashion catalog product photo, sharp fabric texture"
NEGATIVE_PROMPT = "blurry, low quality, distorted, artifacts, noisy"
STEPS = 12

def main():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"=== Stable Diffusion x4 Upscaler ===")
    print(f"Target device: {device}")
    print(f"Inference steps: {STEPS}")
    print(f"Loading pipeline 'stabilityai/stable-diffusion-x4-upscaler'...")

    t0 = time.perf_counter()
    from diffusers import StableDiffusionUpscalePipeline

    pipe = StableDiffusionUpscalePipeline.from_pretrained(
        "stabilityai/stable-diffusion-x4-upscaler",
        torch_dtype=torch.float16
    )
    pipe = pipe.to(device)
    # Enable attention slicing, VAE slicing, and VAE tiling to prevent MPS OOM
    pipe.enable_attention_slicing()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()
    load_time = time.perf_counter() - t0
    print(f"Pipeline loaded in {load_time:.2f}s.\n")

    images = sorted(INPUT_DIR.glob("*.png"))
    total_imgs = len(images)
    times = []

    for i, img_p in enumerate(images, 1):
        out_p = OUTPUT_DIR / f"{img_p.stem}.webp"
        if out_p.exists() and out_p.stat().st_size > 1000:
            print(f"[{i}/{total_imgs}] {img_p.name} -> already exists ({out_p.stat().st_size / 1024:.1f} KB), skipping.")
            continue

        print(f"[{i}/{total_imgs}] Processing {img_p.name} ({img_p.stat().st_size / 1024:.1f} KB)...")
        img = Image.open(img_p).convert("RGB")
        
        t_start = time.perf_counter()
        with torch.inference_mode():
            result = pipe(
                prompt=PROMPT,
                negative_prompt=NEGATIVE_PROMPT,
                image=img,
                num_inference_steps=STEPS,
                guidance_scale=6.0
            ).images[0]
        
        t_elapsed = time.perf_counter() - t_start
        times.append(t_elapsed)

        result.save(out_p, format="WEBP", quality=90)
        size_kb = out_p.stat().st_size / 1024
        print(f"  ✓ Saved {out_p.name} ({result.size[0]}x{result.size[1]}, {size_kb:.1f} KB) in {t_elapsed:.2f}s")

        if device == "mps":
            torch.mps.empty_cache()

    if times:
        avg_t = sum(times) / len(times)
        print(f"\nFinished processing {len(times)} images.")
        print(f"Average time per image: {avg_t:.2f}s")
        print(f"Estimated time for 10,000 images: {avg_t * 10000 / 3600:.2f} hours")
    else:
        print("\nAll images were already processed.")

if __name__ == "__main__":
    main()
