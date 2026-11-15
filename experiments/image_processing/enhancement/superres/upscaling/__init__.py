"""4x upscaling methods and the batch runner."""

from .methods import METHOD_IDS, create_upscaler
from .runner import RunStats, run_upscaler

__all__ = ["METHOD_IDS", "create_upscaler", "RunStats", "run_upscaler"]
