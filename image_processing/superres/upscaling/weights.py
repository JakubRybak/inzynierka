"""Model weight files (.pth) stored locally in `models/` and downloaded on demand."""

import urllib.request
from dataclasses import dataclass
from pathlib import Path

from ..paths import MODELS_DIR


@dataclass(frozen=True)
class WeightsFile:
    filename: str
    url: str

    @property
    def path(self) -> Path:
        return MODELS_DIR / self.filename

    def ensure_downloaded(self) -> Path:
        """Download the file if it is not present yet and return its local path."""
        if not self.path.exists():
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            print(f"Downloading {self.filename} from {self.url} ...")
            request = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request) as response, open(self.path, "wb") as file:
                file.write(response.read())
            print(f"  ✓ Saved {self.path}")
        return self.path


REALESRGAN_X4PLUS = WeightsFile(
    "RealESRGAN_x4plus.pth",
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
)
ULTRASHARP_X4 = WeightsFile(
    "4x-UltraSharp.pth",
    "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth",
)
REALWEBPHOTO_DAT2 = WeightsFile(
    "4xRealWebPhoto_v4_dat2.pth",
    "https://huggingface.co/dseditor/UpscaleModels/resolve/main/4xRealWebPhoto_v4_dat2.pth",
)
GFPGAN_V1_4 = WeightsFile(
    "GFPGANv1.4.pth",
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
)
