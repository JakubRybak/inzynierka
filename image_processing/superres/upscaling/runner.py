"""Batch runner: upscales a list of images with one method, saves WebP files and measures latency."""

import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from ..paths import UPSCALED_IMAGES_DIR, upscaled_image_path
from .methods.base import Upscaler

WEBP_QUALITY = 90


@dataclass
class RunStats:
    method_id: str
    processed: int
    skipped: int
    total_seconds: float
    average_kb: float

    @property
    def average_seconds(self) -> float:
        return self.total_seconds / self.processed if self.processed else 0.0

    @property
    def hours_per_10k(self) -> float:
        return self.average_seconds * 10_000 / 3600

    def summary(self) -> str:
        if not self.processed:
            return f"  • {self.method_id}: nothing to do ({self.skipped} already upscaled)"
        return (
            f"  • {self.method_id}: {self.processed} images | "
            f"avg {self.average_seconds * 1000:.0f} ms/img | avg {self.average_kb:.1f} KB | "
            f"~{self.hours_per_10k:.1f} h per 10k images | skipped {self.skipped}"
        )


def run_upscaler(
    upscaler: Upscaler,
    images: list[Path],
    output_root: Path = UPSCALED_IMAGES_DIR,
    force: bool = False,
) -> RunStats:
    """Upscale `images` with an already loaded `upscaler`.

    Existing outputs are skipped unless `force` is set, so interrupted runs can be resumed.
    """
    todo = [p for p in images if force or not upscaled_image_path(upscaler.id, p.stem, output_root).exists()]
    stats = RunStats(upscaler.id, processed=0, skipped=len(images) - len(todo), total_seconds=0.0, average_kb=0.0)
    if not todo:
        return stats

    upscaler.warmup(Image.open(todo[0]).convert("RGB"))

    sizes_kb: list[float] = []
    for index, image_path in enumerate(todo, 1):
        image = Image.open(image_path).convert("RGB")

        start = time.perf_counter()
        result = upscaler.upscale(image)
        elapsed = time.perf_counter() - start

        out_path = upscaled_image_path(upscaler.id, image_path.stem, output_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        result.save(out_path, format="WEBP", quality=WEBP_QUALITY)

        size_kb = out_path.stat().st_size / 1024
        sizes_kb.append(size_kb)
        stats.processed += 1
        stats.total_seconds += elapsed
        print(f"  [{index}/{len(todo)}] {image_path.name} -> {result.width}x{result.height}, "
              f"{size_kb:.1f} KB in {elapsed:.2f}s")

    stats.average_kb = sum(sizes_kb) / len(sizes_kb)
    return stats
