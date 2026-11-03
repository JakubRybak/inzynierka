"""Build independent image/description vectors with resumable spending guards."""
import argparse
import fcntl
import json
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from ..data import load_inputs
from ..settings import load_settings
from ..storage import digest, write_json
from .client import EmbeddingClient


def inputs_for(settings, limit):
    ids, source, images, references, _, _ = load_inputs(settings, limit)
    ids = list(dict.fromkeys(ids + [r['product_id'] for r in references]))
    inputs = []
    for pid in ids:
        main = images[pid][0]
        if main['pose'] != 'id_gridfs_1':
            raise ValueError(f'Unexpected main-image pose for {pid}')
        if not source[pid]['description'].strip():
            raise ValueError(f'Empty description for {pid}')
        for modality in ['image', 'text']:
            content = Path(main['path']).read_bytes() if modality == 'image' else source[pid]['description'].encode()
            inputs.append({'product_id': pid, 'modality': modality, 'content': content,
                           'input_sha256': digest(content), 'image_id': main['image_id'], 'image_path': main['path']})
    return inputs


def build(settings, limit=None, execute=False):
    folder = Path(settings['embeddings'])
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / '.run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return encode(settings, folder, limit, execute)


def encode(settings, folder, limit, execute):
    cfg = settings['embedding_api']
    inputs = inputs_for(settings, limit)
    # Match the previous cache identity when using the same model and input recipe.
    recipe = {'project': settings['api']['project'], 'model': cfg['model'], 'location': settings['api']['location'],
              'output_dimensionality': cfg['dimension'], 'task_type': None,
              'text_input': 'description only, verbatim, no instruction prefix',
              'image_input': 'first source CSV image, original PNG bytes',
              'normalization': 'L2 float32 before Parquet export'}
    fingerprint = digest(json.dumps(recipe, sort_keys=True).encode())
    ledger_path = folder / 'cost_ledger.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    rows = {'image': [], 'text': []}
    client = None
    missing = 0
    for item in inputs:
        pid, modality = item['product_id'], item['modality']
        path = folder / 'cache' / modality / f'{pid}.json'
        if path.exists():
            cached = json.loads(path.read_text())
            if cached['settings_sha256'] != fingerprint or cached['input_sha256'] != item['input_sha256']:
                raise ValueError(f'Stale embedding cache for {pid}/{modality}; choose a new embedding folder')
        else:
            missing += 1
            if not execute:
                continue
            if any(r['product_id'] == pid and r['modality'] == modality for r in ledger):
                raise RuntimeError(f'Prior uncertain embedding for {pid}/{modality}; inspect ledger before paying again')
            rate = cfg[f'{modality}_usd_per_million'] / 1_000_000
            reservation = cfg['max_input_tokens'] * rate
            if sum(r['accounted_usd'] for r in ledger) + reservation > cfg['budget_usd']:
                raise RuntimeError('Persistent embedding budget guard reached')
            if client is None:
                client = EmbeddingClient(settings['api'], cfg)
            entry = {'product_id': pid, 'modality': modality, 'status': 'reserved',
                     'settings_sha256': fingerprint, 'input_sha256': item['input_sha256'], 'accounted_usd': reservation}
            ledger.append(entry)
            write_json(ledger_path, ledger)
            try:
                data = client.encode(item['content'], modality)
                values = data['embedding']['values']
                tokens = data['usageMetadata']['promptTokenCount']
                vector = np.asarray(values, dtype=np.float32)
                if (vector.shape != (cfg['dimension'],) or not np.isfinite(vector).all()
                        or np.linalg.norm(vector) <= 0 or data.get('truncated')
                        or not 0 < tokens <= cfg['max_input_tokens']):
                    raise ValueError('Invalid embedding response or usage')
                cached = {'settings_sha256': fingerprint, 'input_sha256': item['input_sha256'],
                          'values': values, 'usage': data['usageMetadata']}
                write_json(path, cached)
                entry.update(status='completed', input_tokens=tokens, accounted_usd=tokens * rate)
                write_json(ledger_path, ledger)
            except Exception as error:
                entry.update(status='failed_or_uncertain', error=str(error))
                write_json(ledger_path, ledger)
                raise
        vector = np.asarray(cached['values'], dtype=np.float32)
        if vector.shape != (cfg['dimension'],) or not np.isfinite(vector).all() or np.linalg.norm(vector) <= 0:
            raise ValueError(f'Invalid cached embedding for {pid}')
        vector /= np.linalg.norm(vector)
        row = {'product_id': pid, 'embedding': vector.tolist(), 'input_sha256': item['input_sha256']}
        if modality == 'image':
            row.update(image_id=item['image_id'], image_path=item['image_path'])
        rows[modality].append(row)
    summary = {'selected_products_including_references': len(inputs) // 2, 'missing_vectors_before_run': missing,
               'cached_vectors': {m: len(r) for m, r in rows.items()}, 'execute': execute}
    if execute:
        expected = len(inputs) // 2
        # Reject subset exports over an existing larger export.
        old_path = folder / 'manifest.json'
        if old_path.exists():
            old = json.loads(old_path.read_text())
            if old.get('expected_per_modality', expected) > expected:
                raise ValueError('Refusing to replace a larger embedding export with a subset')
        for modality, values in rows.items():
            fields = [('product_id', pa.string()), ('embedding', pa.list_(pa.float32(), cfg['dimension'])),
                      ('input_sha256', pa.string())]
            if modality == 'image':
                fields += [('image_id', pa.string()), ('image_path', pa.string())]
            temporary = folder / f'{modality}.parquet.tmp'
            pq.write_table(pa.Table.from_pylist(values, schema=pa.schema(fields)), temporary, compression='zstd')
            temporary.replace(folder / f'{modality}.parquet')
        write_json(old_path, {**recipe, 'settings_sha256': fingerprint, 'expected_per_modality': expected,
                              'counts': {m: len(r) for m, r in rows.items()},
                              'complete': all(len(r) == expected for r in rows.values()),
                              'estimated_cost_usd': sum(r['accounted_usd'] for r in ledger)})
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--execute', action='store_true', help='Authorize paid embedding requests')
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be positive')
    print(json.dumps(build(load_settings(args.config), args.limit, args.execute), indent=2))


if __name__ == '__main__':
    main()
