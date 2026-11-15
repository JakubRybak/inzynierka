"""Encode a tinted catalog photo for an HTTP response."""

from io import BytesIO
from pathlib import Path

from PIL import Image

from .composite import tint_background


def render_webp(photo_path: Path, mask_path: Path) -> bytes:
    """Read one photo and its matching mask and return WebP bytes."""
    with Image.open(photo_path) as photo, Image.open(mask_path) as mask:
        result = tint_background(photo.convert("RGB"), mask)
    with BytesIO() as buffer:
        result.save(buffer, format="WEBP", lossless=True)
        return buffer.getvalue()
