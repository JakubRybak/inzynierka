"""Load repository-relative paths without depending on the shell directory."""
from pathlib import Path

from .config_io import read_yaml

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


def validate_batch_settings(settings):
    batch = settings.get('batch', {})
    bucket = batch.get('bucket')
    if not isinstance(bucket, str) or not bucket or '/' in bucket:
        raise ValueError('Set batch.bucket to an existing Cloud Storage bucket name without gs://')
    prefix = batch.get('prefix')
    if not isinstance(prefix, str) or not prefix.strip('/'):
        raise ValueError('Set a nonempty batch.prefix')
    for key in ('budget_usd', 'poll_seconds', 'input_usd_per_million', 'output_usd_per_million'):
        value = batch.get(key)
        if not isinstance(value, (int, float)) or not 0 < value < float('inf'):
            raise ValueError(f'batch.{key} must be positive and finite')
