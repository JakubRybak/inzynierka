"""Encode the fixed pilot with resumable caches and a persistent spending guard."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import threading
import time

import google.auth
from google.auth.transport.requests import AuthorizedSession
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'poc/feature_extraction/embeddings/gemini_embedding_2'
PROJECT = 'project-3a86f100-1aae-4780-84b'
MODEL = 'gemini-embedding-2'
DIMENSION = 3072
RATES = {'image': 0.45 / 1_000_000, 'text': 0.20 / 1_000_000}
MAX_INPUT_TOKENS = 8192
SETTINGS = {'project': PROJECT, 'model': MODEL, 'location': 'global',
            'output_dimensionality': DIMENSION, 'task_type': None,
            'text_input': 'description only, verbatim, no instruction prefix',
            'image_input': 'first source CSV image, original PNG bytes',
            'normalization': 'L2 float32 before Parquet export'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False) + '\n')
    tmp.replace(path)


def load_inputs():
    sample_path = ROOT / 'poc/feature_extraction/samples/pilot_900/products.csv'
    with sample_path.open(newline='') as f:
        pilot = list(csv.DictReader(f))
    assert len(pilot) == len({r['product_id'] for r in pilot}) == 900
    with (ROOT / 'data/processed/fashiongen/products_train.csv').open(newline='') as f:
        source = {r['product_id']: r for r in csv.DictReader(f)}
    images = {}
    with (ROOT / 'data/processed/fashiongen/images_train.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            images.setdefault(row['product_id'], row)
    inputs = []
    for r in pilot:
        pid = r['product_id']; raw = source[pid]; im = images[pid]
        assert r['split'] == 'train' and raw['category'] == r['category']
        assert raw['description'].strip()
        path = 'data/processed/fashiongen/' + im['image_path']
        assert im['pose'] == 'id_gridfs_1', 'Unexpected first-image pose; inspect before paying'
        with Image.open(ROOT / path) as image:
            assert image.size == (256, 256) and image.format == 'PNG'
        for modality, content in [('image', (ROOT / path).read_bytes()), ('text', raw['description'].encode('utf-8'))]:
            inputs.append({'product_id': pid, 'category': r['category'], 'modality': modality,
                           'input_sha256': digest(content),
                           'image_id': im['image_id'] if modality == 'image' else None,
                           'image_path': path if modality == 'image' else None,
                           'content': content})
    return inputs, digest(sample_path.read_bytes())


def export(inputs, fingerprint, ledger, pilot_hash):
    counts = {}
    for modality in ('image', 'text'):
        rows = []
        for item in inputs:
            if item['modality'] != modality:
                continue
            path = OUT / 'cache' / modality / (item['product_id'] + '.json')
            if not path.exists():
                continue
            cached = json.loads(path.read_text())
            assert cached['settings_sha256'] == fingerprint and cached['input_sha256'] == item['input_sha256']
            vector = np.asarray(cached['values'], dtype=np.float32)
            assert vector.shape == (DIMENSION,) and np.isfinite(vector).all() and np.linalg.norm(vector) > 0
            vector /= np.linalg.norm(vector)
            row = {'product_id': item['product_id'], 'embedding': vector.tolist(), 'input_sha256': item['input_sha256']}
            if modality == 'image':
                row.update(image_id=item['image_id'], image_path=item['image_path'])
            rows.append(row)
        fields = [('product_id', pa.string()), ('embedding', pa.list_(pa.float32(), DIMENSION)), ('input_sha256', pa.string())]
        if modality == 'image': fields += [('image_id', pa.string()), ('image_path', pa.string())]
        table = pa.Table.from_pylist(rows, schema=pa.schema(fields))
        tmp = OUT / (modality + '.parquet.tmp')
        pq.write_table(table, tmp, compression='zstd'); tmp.replace(OUT / (modality + '.parquet'))
        counts[modality] = len(rows)
    atomic_json(OUT / 'manifest.json', {
        **SETTINGS, 'settings_sha256': fingerprint, 'pilot_sha256': pilot_hash,
        'generated_at_utc': now(), 'counts': counts, 'expected_per_modality': 900,
        'complete': counts == {'image': 900, 'text': 900},
        'rates_usd_per_million_input_tokens': {k: v * 1_000_000 for k, v in RATES.items()},
        'pricing_source': 'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing',
        'pricing_checked_date': '2026-10-25',
        'estimated_cost_usd': sum(e['accounted_usd'] for e in ledger),
        'estimated_successful_cost_usd': sum(e['accounted_usd'] for e in ledger if e['status'] == 'completed'),
        'retained_failure_reservations_usd': sum(e['accounted_usd'] for e in ledger if e['status'] != 'completed'),
        'cost_note': 'Usage tokens times published rates, not a billing invoice; pending/failed requests retain worst-case reservations.',
        'tokens_by_modality': {m: sum(e.get('input_tokens', 0) for e in ledger if e['modality'] == m) for m in RATES},
        'calls_by_status': {s: sum(e['status'] == s for e in ledger) for s in {e['status'] for e in ledger}},
    })
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=3, help='Number of products, two embeddings each; 900 for full pilot')
    parser.add_argument('--budget-usd', type=float, default=0.25)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--retry-uncertain', action='append', default=[], metavar='PRODUCT_ID:MODALITY', help='Explicitly retry an inspected uncertain request, retaining its cost reservation')
    parser.add_argument('--retry-rate-limited', action='store_true', help='Explicitly permit another attempt after a confirmed HTTP 429')
    parser.add_argument('--request-interval', type=float, default=0.0, help='Minimum seconds between request starts across all workers')
    args = parser.parse_args()
    if not 1 <= args.limit <= 900 or not 0 < args.budget_usd <= 0.25 or not 1 <= args.workers <= 4 or args.request_interval < 0:
        parser.error('Limits: 900 products, $0.25 total, 4 workers')
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / '.run.lock').open('w') as run_lock:
        fcntl.flock(run_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        execute(args)


def execute(args):
    inputs, pilot_hash = load_inputs()
    fingerprint = digest(json.dumps(SETTINGS, sort_keys=True).encode())
    for modality in RATES: (OUT / 'cache' / modality).mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / 'manifest.json'
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        assert old['settings_sha256'] == fingerprint and old['pilot_sha256'] == pilot_hash, 'Existing run configuration differs'
    ledger_path = OUT / 'cost_ledger.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    # Start with one product from each category, then retain sample order.
    product_order = []
    seen_categories = set()
    for item in inputs:
        if item['category'] not in seen_categories:
            seen_categories.add(item['category']); product_order.append(item['product_id'])
    product_order += list(dict.fromkeys(i['product_id'] for i in inputs if i['product_id'] not in product_order))
    selected = set(product_order[:args.limit])
    work = []
    for item in inputs:
        if item['product_id'] not in selected: continue
        cache = OUT / 'cache' / item['modality'] / (item['product_id'] + '.json')
        if cache.exists():
            old = json.loads(cache.read_text())
            assert old['settings_sha256'] == fingerprint and old['input_sha256'] == item['input_sha256']
            continue
        previous = [e for e in ledger if e['product_id'] == item['product_id'] and e['modality'] == item['modality']]
        allow_rate_retry = args.retry_rate_limited and all(e.get('error', '').startswith('HTTP 429:') for e in previous)
        allow_uncertain_retry = f"{item['product_id']}:{item['modality']}" in args.retry_uncertain
        if previous and not (allow_rate_retry or allow_uncertain_retry):
            raise RuntimeError('Previous paid attempt without cache; inspect ledger, never retry automatically')
        work.append(item)
    if not work:
        print('All selected vectors cached.', export(inputs, fingerprint, ledger, pilot_hash)); return
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id=PROJECT)
    credentials = credentials.with_quota_project(PROJECT)
    # Refresh before reserving paid work. Never print tokens.
    from google.auth.transport.requests import Request
    credentials.refresh(Request())
    endpoint = f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:embedContent'
    lock = threading.Lock(); stop = threading.Event(); local = threading.local()
    done = 0
    rate_lock = threading.Lock()
    last_start = [0.0]
    def encode(item):
        nonlocal done
        if stop.is_set(): return
        with rate_lock:
            delay = args.request_interval - (time.monotonic() - last_start[0])
            if delay > 0:
                stop.wait(delay)
            if stop.is_set(): return
            last_start[0] = time.monotonic()
        modality = item['modality']; reservation = MAX_INPUT_TOKENS * RATES[modality]
        with lock:
            if stop.is_set(): return
            if sum(e['accounted_usd'] for e in ledger) + reservation > args.budget_usd:
                stop.set(); raise RuntimeError('Persistent budget guard reached')
            entry = {'product_id': item['product_id'], 'modality': modality, 'input_sha256': item['input_sha256'],
                     'settings_sha256': fingerprint, 'started_at_utc': now(), 'status': 'reserved', 'accounted_usd': reservation}
            ledger.append(entry); atomic_json(ledger_path, ledger)
        try:
            if not hasattr(local, 'session'):
                local.session = AuthorizedSession(credentials, max_refresh_attempts=0)
            part = {'text': item['content'].decode('utf-8')} if modality == 'text' else {
                'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(item['content']).decode()}}
            start = time.monotonic()
            response = local.session.post(endpoint, json={'content': {'parts': [part]}, 'outputDimensionality': DIMENSION}, timeout=90)
            if not response.ok:
                raise RuntimeError(f'HTTP {response.status_code}: {response.text[:500]}')
            data = response.json()
            values = data.get('embedding', {}).get('values')
            usage = data.get('usageMetadata', {})
            tokens = usage.get('promptTokenCount')
            vector = np.asarray(values, dtype=np.float32)
            if vector.shape != (DIMENSION,) or not np.isfinite(vector).all() or np.linalg.norm(vector) <= 0:
                raise RuntimeError('Invalid embedding vector')
            if data.get('truncated') or tokens is None or not 0 < tokens <= MAX_INPUT_TOKENS:
                raise RuntimeError('Missing/invalid usage or truncated input')
            cache = {k: v for k, v in item.items() if k != 'content'}
            cache.update(settings_sha256=fingerprint, values=values, usage=usage, input_tokens=tokens)
            atomic_json(OUT / 'cache' / modality / (item['product_id'] + '.json'), cache)
            with lock:
                entry.update(status='completed', input_tokens=tokens, usage=usage,
                             accounted_usd=tokens * RATES[modality], seconds=time.monotonic()-start)
                atomic_json(ledger_path, ledger); done += 1
                if done % 25 == 0 or len(work) <= 6:
                    print(f'{done}/{len(work)} new vectors; estimated total ${sum(e["accounted_usd"] for e in ledger):.6f}', flush=True)
        except Exception as exc:
            stop.set()
            with lock:
                entry.update(status='failed_or_uncertain', error=str(exc)[:600]); atomic_json(ledger_path, ledger)
            raise
    error = None
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(encode, item) for item in work]
        for future in as_completed(futures):
            try: future.result()
            except Exception as exc:
                stop.set(); error = error or exc
    counts = export(inputs, fingerprint, ledger, pilot_hash)
    print('Saved:', counts, 'estimated USD:', sum(e['accounted_usd'] for e in ledger), flush=True)
    if error: raise RuntimeError('Stopped without retries: ' + str(error))


if __name__ == '__main__': main()
