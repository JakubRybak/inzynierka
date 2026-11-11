"""Registry of all upscaling methods, keyed by method id.

The id is also the output folder name (`outputs/images/<id>/`) and the key used by the report.
"""

from typing import Callable

from ..weights import REALWEBPHOTO_DAT2
from .base import Upscaler
from .dat2_gfpgan import Dat2GfpganUpscaler
from .lanczos import LanczosUpscaler
from .spandrel_model import SpandrelUpscaler
from .stable_diffusion import StableDiffusionUpscaler

_FACTORIES: dict[str, Callable[[], Upscaler]] = {
    "lanczos": LanczosUpscaler,
    "dat2": lambda: SpandrelUpscaler("dat2", "4xRealWebPhoto DAT-2", REALWEBPHOTO_DAT2),
    "dat2_gfpgan": Dat2GfpganUpscaler,
    "sd_x4": StableDiffusionUpscaler,
}

METHOD_IDS: list[str] = list(_FACTORIES)


def create_upscaler(method_id: str) -> Upscaler:
    try:
        return _FACTORIES[method_id]()
    except KeyError:
        raise ValueError(f"Unknown method '{method_id}'. Available: {', '.join(METHOD_IDS)}") from None
