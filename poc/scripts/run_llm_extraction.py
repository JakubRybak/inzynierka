"""Small synchronous PoC extraction with persisted requests and spending guard."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import time

import google.auth
from google.auth.transport.requests import AuthorizedSession, Request
import pyarrow as pa
import pyarrow.parquet as pq

from llm_pipeline import Dataset, ROOT
from build_prompt import requested_rules

PROJECT = 'project-3a86f100-1aae-4780-84b'
MODEL = 'gemini-3.5-flash-lite'
INPUT_RATE = 0.30 / 1_000_000
OUTPUT_RATE = 2.50 / 1_000_000
MAX_OUTPUT = 8192


def write_json(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def export(folder, results):
    ordered = list(results.values())
    (folder / 'products.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in ordered))
    if ordered:
        nested = ['features', 'feature_metadata', 'exclusion_reasons', 'outside_schema_reasons', 'llm_metadata']
        columns = list(ordered[0])
        rows = [{k: json.dumps(r[k], ensure_ascii=False, sort_keys=True) if k in nested else r[k] for k in columns} for r in ordered]
        table = pa.Table.from_pylist(rows, schema=pa.schema([(k, pa.string()) for k in columns]))
        pq.write_table(table, folder / 'products.parquet', compression='zstd')
        decoded = pq.read_table(folder / 'products.parquet').to_pylist()
        for row in decoded:
            for key in nested: row[key] = json.loads(row[key])
        if decoded != ordered: raise ValueError('Parquet/JSONL mismatch')


def export_bank(folder, dataset):
    path = folder / 'reference_bank.jsonl'
    tmp = path.with_suffix('.tmp')
    tmp.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in dataset.bank.values()))
    tmp.replace(path)


def api_body(prompt):
    parts, image_manifest = [], []
    for part in prompt['parts']:
        if 'text' in part:
            parts.append(part)
        else:
            path = part['local_image_path']; content = (ROOT / path).read_bytes()
            image_manifest.append({'path': path, 'sha256': hashlib.sha256(content).hexdigest()})
            parts.append({'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(content).decode()}})
    config = {**prompt['generation_config'], 'maxOutputTokens': MAX_OUTPUT}
    return {'systemInstruction': {'parts': [{'text': prompt['system_instruction']}]},
            'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': config}, image_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--per-category', type=int, default=2)
    parser.add_argument('--run-name', default='smoke_6')
    parser.add_argument('--execute', action='store_true', help='Enable paid requests; default is offline preparation')
    parser.add_argument('--budget-usd', type=float, default=0.30)
    args = parser.parse_args()
    if not 1 <= args.per_category <= 5 or not 0 < args.budget_usd <= 0.30:
        parser.error('This test runner permits up to 5 products/category and $0.30 total')
    if not args.run_name.replace('_', '').replace('-', '').isalnum():
        parser.error('Invalid run name')
    folder = ROOT / 'poc/feature_extraction/runs' / args.run_name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'calls').mkdir(exist_ok=True)
    with (folder / '.run.lock').open('w') as run_lock:
        fcntl.flock(run_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args, folder)


def run(args, folder):
    dataset = Dataset(); target_ids = dataset.select_targets(args.per_category)
    settings = {'project': PROJECT, 'model': MODEL, 'location': 'global',
                'thinking': 'MEDIUM', 'media_resolution': 'MEDIUM', 'max_output_tokens': MAX_OUTPUT,
                'example_image_poses': ['id_gridfs_1', 'id_gridfs_3']}
    fingerprint = hashlib.sha256(json.dumps({
        'settings': settings, 'system': (ROOT / 'poc/feature_extraction/prompts/system.txt').read_text(),
        'definitions': (ROOT / 'poc/feature_extraction/prompts/feature_definitions.json').read_text(),
        'reference_hash': hashlib.sha256((ROOT / 'poc/feature_extraction/reference/products.jsonl').read_bytes()).hexdigest(),
        'embedding_settings': dataset.embedding_manifest['settings_sha256'],
        'code_hashes': {name: hashlib.sha256((ROOT / 'poc/scripts' / name).read_bytes()).hexdigest()
                        for name in ['llm_pipeline.py', 'build_prompt.py']},
        'config_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT / 'extraction/config').rglob('*.yaml'))},
    }, sort_keys=True).encode()).hexdigest()
    manifest = {'settings': settings, 'fingerprint': fingerprint, 'target_ids': target_ids,
                'budget_usd': args.budget_usd, 'initial_bank_size': len(dataset.bank),
                'rates_usd_per_million': {'input': .30, 'output_including_thinking': 2.50},
                'pricing_source': 'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing'}
    manifest_path = folder / 'manifest.json'
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        if old['fingerprint'] != fingerprint or old['target_ids'] != target_ids:
            raise ValueError('Existing run differs; use a new run-name rather than mix versions')
    write_json(manifest_path, manifest)
    results_path = folder / 'products.jsonl'
    results = {r['product_id']: r for r in map(json.loads, results_path.read_text().splitlines())} if results_path.exists() else {}
    session = None
    if args.execute:
        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id=PROJECT)
        credentials.refresh(Request())
        session = AuthorizedSession(credentials.with_quota_project(PROJECT), max_refresh_attempts=0)
    endpoint = f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}'
    for pid in target_ids:
        if pid in results:
            dataset.add_reference(results[pid]); continue
        path = folder / 'calls' / (pid + '.json')
        if path.exists(): raise RuntimeError(f'Prior attempt for {pid}; inspect before retrying')
        prompt, neighbors = dataset.prompt(pid)
        body, image_manifest = api_body(prompt)
        if len(image_manifest) != len(dataset.images[pid]) + 4:
            raise ValueError('Expected all target images and exactly four reference images')
        rules = requested_rules(dataset.keywords[pid])
        expected = set(rules)
        if set(body['generationConfig']['responseSchema']['properties']['features']['properties']) != expected:
            raise ValueError('Schema differs from missing features')
        for part in prompt['parts']:
            if part.get('text', '').startswith(('REFERENCE 1\n', 'REFERENCE 2\n')):
                labels = json.loads(part['text'].split('\n', 1)[1])['labels']
                if set(labels) != expected: raise ValueError('Example leaked assigned feature labels')
        request_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        request_path = folder / 'calls' / (pid + '_prompt.json')
        write_json(request_path, prompt)
        print(pid, dataset.keywords[pid]['category'], list(rules), 'neighbors', [n['product_id'] for n in neighbors],
              'images', len(image_manifest), flush=True)
        if not args.execute: continue
        # Count before inference. Schema tokens receive an extra conservative
        # UTF-8-byte allowance because countTokens may exclude output schemas.
        counted = session.post(endpoint + ':countTokens', json={
            'contents': body['contents'], 'systemInstruction': body['systemInstruction'],
            'generationConfig': body['generationConfig']}, timeout=60)
        if not counted.ok: raise RuntimeError(f'countTokens HTTP {counted.status_code}: {counted.text[:500]}')
        token_count = counted.json()['totalTokens']
        schema_allowance = len(json.dumps(body['generationConfig']['responseSchema']).encode())
        if token_count > 20000: raise RuntimeError('Unexpectedly large prompt; stopped before inference')
        reservation = (token_count + schema_allowance + 2048) * INPUT_RATE + MAX_OUTPUT * OUTPUT_RATE
        calls = [json.loads(p.read_text()) for p in (folder / 'calls').glob('*.json') if not p.name.endswith('_prompt.json')]
        spent = sum(c['accounted_usd'] for c in calls)
        if spent + reservation > args.budget_usd: raise RuntimeError('Budget guard reached before inference')
        call = {'call_id': f'{args.run_name}/{pid}', 'product_id': pid, 'status': 'reserved',
                'started_at_utc': datetime.now(timezone.utc).isoformat(), 'accounted_usd': reservation,
                'reservation_usd': reservation, 'model': MODEL, 'request_sha256': request_hash,
                'prompt_fingerprint': fingerprint, 'neighbors': neighbors, 'bank_size': len(dataset.bank),
                'images': image_manifest, 'requested_features': list(rules), 'count_tokens_response': counted.json()}
        write_json(path, call)
        start = time.monotonic()
        try:
            response = session.post(endpoint + ':generateContent', json=body, timeout=180)
            call.update(seconds=time.monotonic()-start, http_status=response.status_code, response=response.json())
            write_json(path, call)
            if not response.ok: raise RuntimeError(f'generateContent HTTP {response.status_code}: {response.text[:500]}')
            usage = call['response']['usageMetadata']
            if 'promptTokenCount' not in usage or 'candidatesTokenCount' not in usage:
                raise ValueError('Missing token usage; keep reservation')
            cost = usage['promptTokenCount'] * INPUT_RATE + (usage['candidatesTokenCount'] + usage.get('thoughtsTokenCount', 0)) * OUTPUT_RATE
            call.update(usage=usage, estimated_usd=cost, accounted_usd=cost)
            candidate = call['response']['candidates'][0]
            if candidate.get('finishReason') != 'STOP': raise ValueError('Incomplete or blocked response')
            text = ''.join(p.get('text', '') for p in candidate['content']['parts'] if not p.get('thought'))
            parsed = json.loads(text); call['parsed_output'] = parsed
            result = dataset.result(pid, parsed, {
                'call_id': call['call_id'], 'model': MODEL, 'prompt_fingerprint': fingerprint,
                'request_sha256': request_hash, 'neighbors': neighbors, 'bank_size_before': len(dataset.bank),
                'generation_config': body['generationConfig'], 'usage': usage, 'estimated_usd': cost})
            results[pid] = result; export(folder, results)
            dataset.add_reference(result)
            export_bank(folder, dataset)
            call.update(status='completed', result_status=result['status'])
            write_json(path, call)
            print('  saved', result['status'], 'USD', round(cost, 7), flush=True)
        except Exception as exc:
            call.update(status='needs_inspection', error=str(exc)[:800]); write_json(path, call)
            raise
    if args.execute:
        export(folder, results)
        export_bank(folder, dataset)
        calls = [json.loads(p.read_text()) for p in (folder / 'calls').glob('*.json') if not p.name.endswith('_prompt.json')]
        summary = {'planned': len(target_ids), 'completed': len(results),
                   'statuses': dict(Counter(r['status'] for r in results.values())),
                   'accounted_usd': sum(c['accounted_usd'] for c in calls), 'final_bank_size': len(dataset.bank)}
        write_json(folder / 'summary.json', summary)
        print(summary, flush=True)


if __name__ == '__main__': main()
