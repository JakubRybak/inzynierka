"""Validate and atomically write grayscale PNG masks."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image


def valid_mask(path: Path, size: tuple[int, int]) -> bool:
    try:
        with Image.open(path) as mask:
            if mask.format != "PNG" or mask.mode != "L" or mask.size != size:
                return False
            mask.load()
            return True
    except OSError:
        return False


def save_mask(mask: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            mask.save(handle, format="PNG")
            handle.close()
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
