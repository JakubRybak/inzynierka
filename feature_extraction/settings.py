"""Load repository-relative paths without depending on the shell directory."""
from pathlib import Path

from .config_io import read_yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(__file__).resolve().parent


def resolve_path(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def validate_embedding_settings(cfg):
    cfg = cfg.copy() if cfg else {}
    cfg.setdefault('concurrency', 1)
    cfg.setdefault('max_rate_limit_retries', 5)
    cfg.setdefault('max_auth_retries', 2)
    concurrency = cfg['concurrency']
    if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
        raise ValueError('embedding_api.concurrency must be an integer >= 1')
    for key in ('max_rate_limit_retries', 'max_auth_retries'):
        value = cfg[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f'embedding_api.{key} must be an integer >= 0')
    return cfg


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
    if 'embedding_api' in settings:
        settings['embedding_api'] = validate_embedding_settings(settings['embedding_api'])
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
