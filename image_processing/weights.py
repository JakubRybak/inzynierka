"""Download the two model checkpoints on first use."""

from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

DEFAULT_WEIGHTS_DIR = Path(__file__).resolve().parent / "models"
DAT2_WEIGHTS = (
    "4xRealWebPhoto_v4_dat2.pth",
    "https://huggingface.co/dseditor/UpscaleModels/resolve/main/4xRealWebPhoto_v4_dat2.pth",
)
GFPGAN_WEIGHTS = (
    "GFPGANv1.4.pth",
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
)


def get_checkpoint(directory: Path, checkpoint: tuple[str, str]) -> Path:
    filename, url = checkpoint
    destination = directory / filename
    if destination.is_file() and destination.stat().st_size:
        return destination

    directory.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with NamedTemporaryFile(dir=directory, suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            with urlopen(request, timeout=60) as response:
                copyfileobj(response, handle)
            handle.close()
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    return destination
