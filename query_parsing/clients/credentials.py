"""Read provider credentials from the environment or the repository .env."""

import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_api_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name].strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(f"Missing {name} in environment or .env")
