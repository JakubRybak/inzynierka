"""Join processed product and image manifests by product ID."""
import csv
from pathlib import Path

from .keywords.engine import load_config
from .settings import BASE
from .schema import load_schemas
from .storage import read_jsonl


def load_inputs(settings, limit=None):
    schemas, _ = load_schemas()
    configs, _ = load_config(BASE / 'keywords/definitions', schemas)
    selected = None
    if settings.get('selection'):
        with Path(settings['selection']).open(newline='') as stream:
            selection = list(csv.DictReader(stream))
        selected = [row['product_id'] for row in selection]
        if len(selected) != len(set(selected)):
            raise ValueError('Selection contains duplicate product IDs')
    references = [r for r in read_jsonl(settings['references']) if r['category'] in settings['categories']]
    reference_ids = {row['product_id'] for row in references}
    source, images = {}, {}
    dataset = Path(settings['dataset'])
    for split in settings['splits']:
        with (dataset / f'products_{split}.csv').open(newline='') as stream:
            for row in csv.DictReader(stream):
                pid = row['product_id']
                if selected is not None and pid not in selected and pid not in reference_ids:
                    continue
                if row['category'] not in settings['categories']:
                    continue
                if (row['section'], row['category']) not in schemas:
                    raise ValueError(f'No rules for {row["category"]}')
                if pid in source:
                    raise ValueError(f'Duplicate product ID across dataset: {pid}')
                source[pid] = row
        with (dataset / f'images_{split}.csv').open(newline='') as stream:
            for row in csv.DictReader(stream):
                if row['product_id'] in source:
                    image = {**row, 'path': str((dataset / row['image_path']).resolve())}
                    images.setdefault(row['product_id'], []).append(image)
    target_ids = selected if selected is not None else list(source)
    missing = set(target_ids) - set(source)
    if missing:
        raise ValueError(f'Selected products missing from configured dataset: {sorted(missing)[:10]}')
    if limit is not None:
        target_ids = target_ids[:limit]
    if not target_ids:
        raise ValueError('No products selected')
    return target_ids, source, images, references, configs, schemas
