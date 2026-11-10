"""Renders `outputs/report.html` from Jinja templates.

The output is a single self-contained HTML file: CSS and JS from `templates/` are inlined,
images are referenced by relative paths so the report works when opened straight from disk.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..paths import REPORT_PATH, SAMPLE_IMAGES_DIR, UPSCALED_IMAGES_DIR, list_sample_images, upscaled_image_path
from .methods import COLUMN_FILTERS, DEFAULT_PREVIEW_ID, METHODS, MethodInfo
from .products import SampleImage, load_sample_images

TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass(frozen=True)
class PhotoTone:
    id: str
    label: str
    short_label: str


PHOTO_TONES = [
    PhotoTone("grey-soft", "Szare (#ededf0)", "Szare"),
    PhotoTone("grey-medium", "Średnie (#e2e4e8)", "Średnie"),
    PhotoTone("grey-warm", "Ciepłe (#edeae4)", "Ciepłe"),
    PhotoTone("white", "Białe 100% (#ffffff)", "Białe"),
]
DEFAULT_PHOTO_TONE = "grey-soft"


def build_report(output_path: Path = REPORT_PATH) -> Path:
    samples = load_sample_images(list_sample_images())
    if not samples:
        raise RuntimeError(f"No sample images found in {SAMPLE_IMAGES_DIR}")

    images = _ImageLocator(output_path.parent)
    missing = [f"{m.id}/{s.stem}" for m in METHODS for s in samples if not images.file(m, s).exists()]
    if missing:
        print(f"⚠️  {len(missing)} upscaled images are missing, e.g. {missing[:3]} — run upscale.py first.")

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    html = env.get_template("report.html.j2").render(
        methods=METHODS,
        samples=samples,
        column_filters=COLUMN_FILTERS,
        photo_tones=PHOTO_TONES,
        default_photo_tone=DEFAULT_PHOTO_TONE,
        default_preview_id=DEFAULT_PREVIEW_ID,
        image_src=images.src,
        file_size=images.file_size_label,
        styles=(TEMPLATES_DIR / "styles.css").read_text(encoding="utf-8"),
        script=(TEMPLATES_DIR / "app.js").read_text(encoding="utf-8"),
        app_config=_app_config(images),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


class _ImageLocator:
    """Resolves image files on disk and their URLs relative to the report file."""

    def __init__(self, report_dir: Path):
        self.report_dir = report_dir

    def file(self, method: MethodInfo, sample: SampleImage) -> Path:
        return sample.path if method.is_original else upscaled_image_path(method.id, sample.stem)

    def directory_url(self, method: MethodInfo) -> str:
        directory = SAMPLE_IMAGES_DIR if method.is_original else UPSCALED_IMAGES_DIR / method.id
        return Path(os.path.relpath(directory, self.report_dir)).as_posix()

    def src(self, method: MethodInfo, sample: SampleImage) -> str:
        return f"{self.directory_url(method)}/{sample.stem}.{method.file_format}"

    def file_size_label(self, method: MethodInfo, sample: SampleImage) -> str:
        path = self.file(method, sample)
        return _format_file_size(path.stat().st_size) if path.exists() else "N/A"


def _app_config(images: _ImageLocator) -> dict:
    """Data consumed by app.js (method order defines the 1-8 keyboard shortcuts)."""
    return {
        "defaultMethod": DEFAULT_PREVIEW_ID,
        "methods": [
            {
                "id": m.id,
                "label": f"{m.name} ({m.resolution}px)",
                "imageDir": images.directory_url(m),
                "extension": m.file_format,
                "pixelated": m.is_original,
            }
            for m in METHODS
        ],
        "columnFilters": {f.id: list(f.method_ids) for f in COLUMN_FILTERS},
    }


def _format_file_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"
