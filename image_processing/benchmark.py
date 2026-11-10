"""Benchmark and visual comparison of Super-Resolution methods for fashion e-commerce images.

Evaluates 4 methods:
1. Classical Baseline: Lanczos Resampling (Pillow)
2. Classic CNN SOTA: RealESRGAN_x4plus (ESRGAN)
3. Texture-Focused CNN: 4x-UltraSharp (ESRGAN)
4. Modern Transformer SOTA (2024/2025): 4xRealWebPhoto_v4_dat2 (DAT-2)
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from PIL import Image, ImageFilter
from spandrel import ImageModelDescriptor, ModelLoader
import torch
from torchvision.transforms.functional import to_pil_image, to_tensor

HERE = Path(__file__).resolve().parent
SAMPLE_DIR = HERE / "sample_images"
MODELS_DIR = HERE / "models"
OUTPUTS_DIR = HERE / "outputs"


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


def benchmark_all() -> Dict[str, Any]:
    device = get_device()
    print(f"==================================================")
    print(f"🚀 Benchmarking Image Super-Resolution on: {device}")
    print(f"==================================================")

    loader = ModelLoader()
    images = sorted(list(SAMPLE_DIR.glob("*.png")))
    if not images:
        raise RuntimeError(f"No sample images found in {SAMPLE_DIR}")
    print(f"Found {len(images)} sample images.")

    methods = [
        {
            "id": "bicubic",
            "name": "Lanczos + Unsharp (Classical Baseline)",
            "type": "classical",
            "scale": 4,
            "architecture": "Bicubic/Lanczos Interpolation",
            "model_path": None,
        },
        {
            "id": "realesrgan_x4plus",
            "name": "Real-ESRGAN x4plus",
            "type": "neural",
            "scale": 4,
            "architecture": "ESRGAN / RRDBNet",
            "model_path": MODELS_DIR / "RealESRGAN_x4plus.pth",
        },
        {
            "id": "ultrasharp_x4",
            "name": "4x-UltraSharp",
            "type": "neural",
            "scale": 4,
            "architecture": "ESRGAN (Micro-texture tuned)",
            "model_path": MODELS_DIR / "4x-UltraSharp.pth",
        },
        {
            "id": "realwebphoto_dat2",
            "name": "4xRealWebPhoto (DAT-2)",
            "type": "neural",
            "scale": 4,
            "architecture": "DAT-2 (Dual Aggregation Transformer, 2024)",
            "model_path": MODELS_DIR / "4xRealWebPhoto_v4_dat2.pth",
        },
    ]

    results: Dict[str, Any] = {
        "device": str(device),
        "num_sample_images": len(images),
        "methods": {},
    }

    # Preload neural models
    loaded_models: Dict[str, Any] = {}
    for m in methods:
        if m["type"] == "neural":
            print(f"Loading {m['name']} from {m['model_path'].name}...")
            t0 = time.perf_counter()
            desc = loader.load_from_file(str(m["model_path"]))
            model = desc.to(device).eval()
            loaded_models[m["id"]] = model
            print(f"  ✓ Loaded {m['name']} in {time.perf_counter() - t0:.2f}s")

    for m in methods:
        mid = m["id"]
        out_dir = OUTPUTS_DIR / mid
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nEvaluating: {m['name']} ...")

        # Warmup for neural models
        if m["type"] == "neural":
            dummy = torch.zeros(1, 3, 256, 256, device=device)
            with torch.no_grad():
                _ = loaded_models[mid](dummy)
            sync_device(device)

        latencies_ms: List[float] = []
        file_sizes_webp_kb: List[float] = []
        file_sizes_png_kb: List[float] = []

        for img_path in images:
            img = Image.open(img_path).convert("RGB")

            t_start = time.perf_counter()
            if m["type"] == "classical":
                out_img = run_bicubic(img)
            else:
                t_input = to_tensor(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    t_out = loaded_models[mid](t_input).squeeze(0).clamp(0, 1)
                sync_device(device)
                out_img = to_pil_image(t_out.cpu())
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            latencies_ms.append(t_elapsed_ms)

            # Save as PNG
            png_path = out_dir / f"{img_path.stem}.png"
            out_img.save(png_path, format="PNG")
            file_sizes_png_kb.append(png_path.stat().st_size / 1024.0)

            # Save as WebP (quality=90)
            webp_path = out_dir / f"{img_path.stem}.webp"
            out_img.save(webp_path, format="WEBP", quality=90)
            file_sizes_webp_kb.append(webp_path.stat().st_size / 1024.0)

        total_time_s = sum(latencies_ms) / 1000.0
        avg_ms = float(np.mean(latencies_ms))
        p50_ms = float(np.median(latencies_ms))
        p90_ms = float(np.percentile(latencies_ms, 90))
        extrapolated_10k_min = (avg_ms * 10000) / (1000 * 60)
        extrapolated_10k_hours = extrapolated_10k_min / 60

        print(f"  • Total time ({len(images)} images): {total_time_s:.2f}s")
        print(f"  • Avg latency per image: {avg_ms:.1f} ms (p50: {p50_ms:.1f} ms, p90: {p90_ms:.1f} ms)")
        print(f"  • Estimated time for 10,000 images: {extrapolated_10k_min:.1f} min ({extrapolated_10k_hours:.2f} h)")
        print(f"  • Avg output file size: PNG={np.mean(file_sizes_png_kb):.1f} KB | WebP={np.mean(file_sizes_webp_kb):.1f} KB")

        results["methods"][mid] = {
            "name": m["name"],
            "architecture": m["architecture"],
            "type": m["type"],
            "total_time_seconds": round(total_time_s, 3),
            "avg_ms_per_image": round(avg_ms, 1),
            "p50_ms": round(p50_ms, 1),
            "p90_ms": round(p90_ms, 1),
            "throughput_fps": round(1000.0 / avg_ms, 1),
            "extrapolated_10k_minutes": round(extrapolated_10k_min, 1),
            "extrapolated_10k_hours": round(extrapolated_10k_hours, 2),
            "avg_png_size_kb": round(float(np.mean(file_sizes_png_kb)), 1),
            "avg_webp_size_kb": round(float(np.mean(file_sizes_webp_kb)), 1),
        }

    results_path = OUTPUTS_DIR / "benchmark_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved benchmark results to: {results_path}")

    # Generate visual HTML comparison report
    generate_html_report(images, methods, results)
    return results


def generate_html_report(
    images: List[Path],
    methods: List[Dict[str, Any]],
    results: Dict[str, Any],
) -> None:
    html_path = OUTPUTS_DIR / "comparison_report.html"
    
    # We will embed images as relative paths or base64 so it can be opened easily
    items_html = []
    for i, img_path in enumerate(images):
        stem = img_path.stem
        # Category label from filename: e.g. 01_jacket_86605 -> Jacket (86605)
        parts = stem.split("_")
        cat_title = f"{parts[1].capitalize()} (ID {parts[2]})" if len(parts) >= 3 else stem

        row_html = f"""
        <div class="card" id="card-{i}">
            <h3>{i+1}. {cat_title}</h3>
            <div class="grid">
                <div class="thumb original">
                    <span class="badge">Original (256x256)</span>
                    <img src="../sample_images/{img_path.name}" alt="Original">
                </div>
                <div class="thumb bicubic">
                    <span class="badge">Lanczos Baseline (1024x1024)</span>
                    <img src="bicubic/{stem}.webp" alt="Lanczos">
                </div>
                <div class="thumb realesrgan">
                    <span class="badge">Real-ESRGAN (1024x1024)</span>
                    <img src="realesrgan_x4plus/{stem}.webp" alt="Real-ESRGAN">
                </div>
                <div class="thumb ultrasharp">
                    <span class="badge">4x-UltraSharp (1024x1024)</span>
                    <img src="ultrasharp_x4/{stem}.webp" alt="UltraSharp">
                </div>
                <div class="thumb dat2">
                    <span class="badge highlight">4xRealWebPhoto DAT-2 (1024x1024)</span>
                    <img src="realwebphoto_dat2/{stem}.webp" alt="DAT-2">
                </div>
            </div>
        </div>
        """
        items_html.append(row_html)

    summary_rows = []
    for mid, mdata in results["methods"].items():
        summary_rows.append(f"""
        <tr>
            <td><b>{mdata['name']}</b><br><small>{mdata['architecture']}</small></td>
            <td><b>{mdata['avg_ms_per_image']} ms</b></td>
            <td>{mdata['throughput_fps']} fps</td>
            <td><b>{mdata['extrapolated_10k_minutes']} min</b> ({mdata['extrapolated_10k_hours']} h)</td>
            <td>{mdata['avg_webp_size_kb']} KB</td>
        </tr>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Super-Resolution Comparison (Apple Silicon M1 Pro)</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0f172a;
            color: #f1f5f9;
            margin: 0;
            padding: 24px;
        }}
        h1, h2, h3 {{ color: #ffffff; }}
        .header {{
            max-width: 1400px;
            margin: 0 auto 30px auto;
            border-bottom: 1px solid #334155;
            padding-bottom: 20px;
        }}
        .metrics-table {{
            width: 100%;
            max-width: 1400px;
            margin: 0 auto 40px auto;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }}
        .metrics-table th, .metrics-table td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        .metrics-table th {{
            background: #0f172a;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.05em;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 1px solid #334155;
        }}
        .card h3 {{
            margin-top: 0;
            margin-bottom: 16px;
            font-size: 18px;
            color: #38bdf8;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }}
        @media (max-width: 1100px) {{
            .grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .thumb {{
            position: relative;
            background: #0f172a;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid #334155;
            cursor: pointer;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .thumb:hover {{
            transform: scale(1.02);
            border-color: #38bdf8;
            z-index: 10;
        }}
        .thumb img {{
            width: 100%;
            height: auto;
            aspect-ratio: 1 / 1;
            object-fit: contain;
            display: block;
            image-rendering: auto;
        }}
        .thumb.original img {{
            image-rendering: pixelated;
        }}
        .badge {{
            position: absolute;
            top: 8px;
            left: 8px;
            background: rgba(15, 23, 42, 0.85);
            color: #cbd5e1;
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
            backdrop-filter: blur(4px);
        }}
        .badge.highlight {{
            background: rgba(14, 165, 233, 0.9);
            color: #ffffff;
            font-weight: bold;
        }}
        .instructions {{
            background: #334155;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Porównanie metod podnoszenia rozdzielczości (Super-Resolution)</h1>
        <p>Sprzęt: <b>Apple Silicon M1 Pro (32 GB RAM) · Akceleracja: PyTorch MPS (Metal)</b></p>
        <p>Wejście: zdjęcia produktów 256&times;256 px &rarr; Wyjście: 1024&times;1024 px (skalowanie 4x, format WebP).</p>
    </div>

    <table class="metrics-table">
        <thead>
            <tr>
                <th>Metoda / Architektura</th>
                <th>Średni czas / zdjęcie</th>
                <th>Przepustowość</th>
                <th>Szacowany czas dla 10 000 produktów</th>
                <th>Średni rozmiar WebP</th>
            </tr>
        </thead>
        <tbody>
            {''.join(summary_rows)}
        </tbody>
    </table>

    <div class="container">
        <div class="instructions">
            💡 <b>Wskazówka:</b> Kliknij dowolne zdjęcie prawym przyciskiem myszy i otwórz w nowej karcie, aby zobaczyć je w pełnej rozdzielczości 1024x1024 i przyjrzeć się mikrosplotom tkanin, krawędziom oraz brakowi rozmyć.
        </div>
        {''.join(items_html)}
    </div>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✓ Generated visual HTML comparison report: {html_path}")


if __name__ == "__main__":
    import sys
    if "--report-only" in sys.argv:
        results_path = OUTPUTS_DIR / "benchmark_results.json"
        with open(results_path, "r", encoding="utf-8") as f:
            res = json.load(f)
        imgs = sorted(list(SAMPLE_DIR.glob("*.png")))
        generate_html_report(imgs, None, res)
    else:
        benchmark_all()
