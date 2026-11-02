"""Load repository-relative paths without depending on the shell directory."""
from pathlib import Path

from .keywords.engine import read_yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(__file__).resolve().parent


def resolve_path(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_settings(path=None):
    settings = read_yaml(path or BASE / 'config/extraction.yaml')
    for field in ['dataset', 'selection', 'references', 'embeddings', 'artifacts']:
        if settings.get(field):
            settings[field] = str(resolve_path(settings[field]).resolve())
    api = settings['api']
    if api['budget_usd'] <= 0 or api['max_output_tokens'] <= 0 or api['timeout_seconds'] <= 0:
        raise ValueError('Budget, output limit and timeout must be positive')
    if not 1 <= api['max_attempts'] <= 3:
        raise ValueError('max_attempts must be between 1 and 3')
    return settings
