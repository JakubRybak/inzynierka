"""PyTorch device helpers (Apple Silicon MPS > CUDA > CPU)."""

import torch


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def empty_cache(device: torch.device) -> None:
    """Release cached GPU memory between heavy inferences."""
    if device.type == "mps":
        torch.mps.empty_cache()
    elif device.type == "cuda":
        torch.cuda.empty_cache()
