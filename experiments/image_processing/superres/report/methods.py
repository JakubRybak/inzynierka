"""Display metadata and benchmark results for every method shown in the report.

Timings were measured on Apple Silicon M1 Pro (PyTorch MPS) for 256x256 -> 1024x1024.
"""

from dataclasses import dataclass

ORIGINAL_ID = "original"


@dataclass(frozen=True)
class MethodInfo:
    id: str
    name: str
    time_per_image: str
    time_per_10k: str

    @property
    def is_original(self) -> bool:
        return self.id == ORIGINAL_ID

    @property
    def file_format(self) -> str:
        return "png" if self.is_original else "webp"


METHODS: list[MethodInfo] = [
    MethodInfo(
        id=ORIGINAL_ID,
        name="Oryginał",
        time_per_image="0 ms",
        time_per_10k="0 min",
    ),
    MethodInfo(
        id="lanczos",
        name="Lanczos + Unsharp",
        time_per_image="27.8 ms",
        time_per_10k="4.6 min",
    ),
    MethodInfo(
        id="dat2",
        name="4xRealWebPhoto DAT-2",
        time_per_image="3.16 s",
        time_per_10k="8.8 h",
    ),
    MethodInfo(
        id="dat2_gfpgan",
        name="DAT-2 + GFPGAN",
        time_per_image="3.77 s",
        time_per_10k="10.5 h",
    ),
    MethodInfo(
        id="sd_x4",
        name="Stable Diffusion x4",
        time_per_image="24.50 s",
        time_per_10k="68.1 h",
    ),
]
