"""Filesystem layout of the project (single source of truth for all paths)."""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

SAMPLE_IMAGES_DIR = PROJECT_DIR / "data" / "sample_images"
MODELS_DIR = PROJECT_DIR / "models"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
UPSCALED_IMAGES_DIR = OUTPUTS_DIR / "images"
REPORT_PATH = OUTPUTS_DIR / "report.html"


def list_sample_images() -> list[Path]:
    """Return all input product photos, sorted by filename."""
    return sorted(SAMPLE_IMAGES_DIR.glob("*.png"))


def upscaled_image_path(method_id: str, stem: str, root: Path = UPSCALED_IMAGES_DIR) -> Path:
    """Location of the upscaled WebP for a given method and input image stem."""
    return root / method_id / f"{stem}.webp"
