"""Super-Resolution Pipeline and Benchmark for fashion e-commerce images.

Evaluates 7 practical deployed, hybrid, and generative methods on Apple Silicon M1 Pro / MPS:
1. Classical Baseline: Lanczos + Unsharp Mask (Pillow)
2. Classic CNN: Real-ESRGAN x4plus
3. Texture-Focused CNN: 4x-UltraSharp
4. Vision Transformer: 4xRealWebPhoto DAT-2 (Benchmark Winner)
5. E-Commerce Hybrid: DAT-2 + GFPGAN Face Restoration (RetinaFace + StyleGAN2)
6. Generative GigaGAN: AuraSR-v2 (fal.ai / Aleph Alpha 2025)
7. Latent Diffusion: Stable Diffusion x4 Upscaler (Stability AI)

Produces optimized 1024x1024 WebP images and renders master_comparison_all_methods.html.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from PIL import Image, ImageFilter
from spandrel import ModelLoader
import torch
from torchvision.transforms.functional import to_pil_image, to_tensor

from generate_all_methods_master import build_all_methods_report

HERE = Path(__file__).resolve().parent
SAMPLE_DIR = HERE / "sample_images"
MODELS_DIR = HERE / "models"
OUTPUTS_DIR = HERE / "outputs"

MODEL_DOWNLOADS = {
    "4xRealWebPhoto_v4_dat2.pth": "https://huggingface.co/dseditor/UpscaleModels/resolve/main/4xRealWebPhoto_v4_dat2.pth",
    "4x-UltraSharp.pth": "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth",
    "RealESRGAN_x4plus.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
    "GFPGANv1.4.pth": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
}


def ensure_models() -> None:
    """Download required neural model weights if they are missing."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in MODEL_DOWNLOADS.items():
        dest = MODELS_DIR / filename
        if not dest.exists():
            print(f"Downloading model {filename} from {url} ...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            print(f"✓ Saved {filename}")


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def sync_device(device: torch.device) -> None:
    if device.type == "mps":
        torch.mps.synchronize()
    elif device.type == "cuda":
        torch.cuda.synchronize()


def run_bicubic(img: Image.Image) -> Image.Image:
    """Lanczos 4x upsampling with subtle sharpening."""
    target_size = (img.width * 4, img.height * 4)
    upscaled = img.resize(target_size, resample=Image.Resampling.LANCZOS)
    return upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))


def run_pipeline() -> None:
    ensure_models()
    device = get_device()
    print("==================================================")
    print(f"🚀 Running Super-Resolution Pipeline on: {device}")
    print("==================================================")

    loader = ModelLoader()
    images = sorted(list(SAMPLE_DIR.glob("*.png")))
    if not images:
        raise RuntimeError(f"No sample images found in {SAMPLE_DIR}")
    print(f"Found {len(images)} sample images.")

    standard_methods = [
        {
            "id": "bicubic",
            "name": "Lanczos + Unsharp (Classical Baseline)",
            "type": "classical",
            "model_path": None,
        },
        {
            "id": "realesrgan_x4plus",
            "name": "Real-ESRGAN x4plus",
            "type": "neural",
            "model_path": MODELS_DIR / "RealESRGAN_x4plus.pth",
        },
        {
            "id": "ultrasharp_x4",
            "name": "4x-UltraSharp",
            "type": "neural",
            "model_path": MODELS_DIR / "4x-UltraSharp.pth",
        },
        {
            "id": "realwebphoto_dat2",
            "name": "4xRealWebPhoto (DAT-2)",
            "type": "neural",
            "model_path": MODELS_DIR / "4xRealWebPhoto_v4_dat2.pth",
        },
        {
            "id": "aurasr_v2",
            "name": "AuraSR-v2 (GigaGAN Generative)",
            "type": "aurasr",
            "model_path": None,
        },
    ]

    # Preload neural models
    loaded_models: Dict[str, Any] = {}
    for m in standard_methods:
        if m["type"] == "neural":
            print(f"Loading {m['name']} from {m['model_path'].name}...")
            t0 = time.perf_counter()
            desc = loader.load_from_file(str(m["model_path"]))
            model = desc.to(device).eval()
            loaded_models[m["id"]] = model
            print(f"  ✓ Loaded {m['name']} in {time.perf_counter() - t0:.2f}s")
        elif m["type"] == "aurasr":
            print(f"Loading {m['name']} from fal/AuraSR-v2...")
            t0 = time.perf_counter()
            from huggingface_hub import snapshot_download
            from safetensors.torch import load_file
            from aura_sr import AuraSR
            hf_path = Path(snapshot_download("fal/AuraSR-v2"))
            config = json.loads((hf_path / "config.json").read_text())
            model = AuraSR(config, device=str(device))
            checkpoint = load_file(hf_path / "model.safetensors")
            model.upsampler.load_state_dict(checkpoint, strict=True)
            loaded_models[m["id"]] = model
            print(f"  ✓ Loaded {m['name']} in {time.perf_counter() - t0:.2f}s")

    for m in standard_methods:
        mid = m["id"]
        out_dir = OUTPUTS_DIR / mid
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nProcessing: {m['name']} ...")

        # Warmup for neural models
        if m["type"] == "neural":
            dummy = torch.zeros(1, 3, 256, 256, device=device)
            with torch.no_grad():
                _ = loaded_models[mid](dummy)
            sync_device(device)
        elif m["type"] == "aurasr":
            dummy_img = Image.open(images[0]).convert("RGB")
            _ = loaded_models[mid].upscale_4x_overlapped(dummy_img)
            sync_device(device)

        latencies_ms: List[float] = []
        file_sizes_webp_kb: List[float] = []

        for img_path in images:
            img = Image.open(img_path).convert("RGB")

            t_start = time.perf_counter()
            if m["type"] == "classical":
                out_img = run_bicubic(img)
            elif m["type"] == "aurasr":
                out_img = loaded_models[mid].upscale_4x_overlapped(img)
                sync_device(device)
            else:
                t_input = to_tensor(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    t_out = loaded_models[mid](t_input).squeeze(0).clamp(0, 1)
                sync_device(device)
                out_img = to_pil_image(t_out.cpu())
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            latencies_ms.append(t_elapsed_ms)

            # Save directly as WebP (quality=90)
            webp_path = out_dir / f"{img_path.stem}.webp"
            out_img.save(webp_path, format="WEBP", quality=90)
            file_sizes_webp_kb.append(webp_path.stat().st_size / 1024.0)

        total_time_s = sum(latencies_ms) / 1000.0
        avg_ms = float(np.mean(latencies_ms))
        print(f"  • Total time: {total_time_s:.2f}s | Avg latency: {avg_ms:.1f} ms/img | Avg size: {np.mean(file_sizes_webp_kb):.1f} KB")

    # Run hybrid and diffusion scripts
    print("\nRunning Hybrid DAT-2 + GFPGAN Face Restoration...")
    subprocess.run([sys.executable, str(HERE / "run_dat2_gfpgan.py")], check=True)

    print("\nRunning Stable Diffusion x4 Upscaler...")
    subprocess.run([sys.executable, str(HERE / "run_sd_x4.py")], check=True)

    print("\n✓ All images upscaled. Regenerating master comparison report...")
    build_all_methods_report()


if __name__ == "__main__":
    if "--report-only" in sys.argv:
        build_all_methods_report()
    else:
        run_pipeline()
