"""Renders `outputs/report.html` from Jinja templates.

The output is a single self-contained HTML file: CSS and JS from `templates/` are inlined,
images are referenced by relative paths so the report works when opened straight from disk.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..paths import REPORT_PATH, SAMPLE_IMAGES_DIR, UPSCALED_IMAGES_DIR, list_sample_images, upscaled_image_path
from .methods import METHODS, MethodInfo
from .products import SampleImage, load_sample_images

TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass(frozen=True)
class PhotoTone:
    id: str
    label: str


PHOTO_TONES = [
    PhotoTone("grey-soft", "Szare"),
    PhotoTone("grey-medium", "Średnie"),
    PhotoTone("grey-warm", "Ciepłe"),
    PhotoTone("white", "Białe"),
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
        photo_tones=PHOTO_TONES,
        default_photo_tone=DEFAULT_PHOTO_TONE,
        image_src=images.src,
        styles=(TEMPLATES_DIR / "styles.css").read_text(encoding="utf-8"),
        script=(TEMPLATES_DIR / "app.js").read_text(encoding="utf-8"),
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
