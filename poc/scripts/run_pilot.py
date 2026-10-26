"""Process the remaining pilot sequentially, extending the bank after each valid result."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import time

import google.auth
from google.auth.transport.requests import AuthorizedSession, Request

from llm_pipeline import Dataset, ROOT, CATEGORIES
from build_prompt import requested_rules
from run_llm_extraction import api_body, write_json, export, export_bank, MODEL, PROJECT, INPUT_RATE, OUTPUT_RATE, MAX_OUTPUT

OUT = ROOT / 'poc/feature_extraction/runs/pilot_sync'
RESULTS = ROOT / 'poc/feature_extraction/results'


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def uniform(record, origin):
    keys = ['product_id', 'brand', 'section', 'category', 'features', 'feature_metadata', 'status', 'exclusion_reasons']
    return {**{k: record[k] for k in keys}, 'product_status': record.get('product_status', 'ok'),
            'product_reason': record.get('product_reason', ''),
            'outside_schema_reasons': record.get('outside_schema_reasons', {}),
            'llm_metadata': record.get('llm_metadata', {}), 'annotation_origin': origin}


def checkpoint(dataset, records, seeds, target_ids, calls, complete=False):
    OUT.mkdir(parents=True, exist_ok=True); RESULTS.mkdir(parents=True, exist_ok=True)
    export(OUT, records); export_bank(OUT, dataset)
    combined = {r['product_id']: uniform(r, 'manual' if r['product_id'] in dataset.initial_reference_ids else 'llm') for r in seeds}
    combined.update({pid: uniform(r, 'llm') for pid, r in records.items()})
    export(RESULTS, combined)
    summary = {'planned_new_products': len(target_ids), 'processed_new_products': len(records),
               'total_pilot_products_saved': len(combined), 'statuses': dict(Counter(r['status'] for r in combined.values())),
               'bank_size': len(dataset.bank), 'accounted_usd_new_run': sum(c['accounted_usd'] for c in calls),
               'successful_usage_usd_new_run': sum(c.get('estimated_usd', 0) for c in calls),
               'prior_smoke_cost_usd': .0193236, 'complete': complete,
               'updated_at_utc': datetime.now(timezone.utc).isoformat()}
    write_json(OUT / 'summary.json', summary); write_json(RESULTS / 'summary.json', summary)
    return summary


def failure_record(dataset, pid, message, metadata):
    record = uniform(dataset.keywords[pid], 'llm')
    record.update(status='needs_review', product_status='processing_error', product_reason=message,
                  llm_metadata=metadata)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--budget-usd', type=float, default=5.0)
    parser.add_argument('--limit', type=int, default=834, help='For offline checks; full run defaults to 834')
    parser.add_argument('--accept-code-update', action='store_true', help='Record an inspected code correction in an existing run')
    args = parser.parse_args()
    if not 0 < args.budget_usd <= 5 or not 1 <= args.limit <= 834:
        parser.error('Maximum $5 and 834 new products')
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ['calls', 'records', 'prompts']: (OUT / name).mkdir(exist_ok=True)
    with (OUT / '.run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args)


def run(args):
    dataset = Dataset()
    manual = load_jsonl(ROOT / 'poc/feature_extraction/reference/products.jsonl')
    smoke = load_jsonl(ROOT / 'poc/feature_extraction/runs/smoke_6/products.jsonl')
    if len(manual) != 60 or len(smoke) != 6: raise ValueError('Expected 60 manual and 6 existing LLM products')
    for record in smoke: dataset.add_reference(record)
    seeds = manual + smoke
    seed_ids = {r['product_id'] for r in seeds}
    by_category = {cat: [r['product_id'] for r in dataset.pilot if r['category'] == cat and r['product_id'] not in seed_ids]
                   for cat in CATEGORIES}
    targets = [by_category[cat][i] for i in range(max(map(len, by_category.values())))
               for cat in CATEGORIES if i < len(by_category[cat])]
    if len(targets) != 834 or len(set(targets)) != 834: raise ValueError('Expected exactly 834 distinct remaining products')
    files = [ROOT / 'poc/feature_extraction/prompts/system.txt', ROOT / 'poc/feature_extraction/prompts/feature_definitions.json',
             ROOT / 'poc/feature_extraction/reference/products.jsonl', ROOT / 'poc/feature_extraction/runs/smoke_6/products.jsonl',
             ROOT / 'poc/feature_extraction/samples/pilot_900/products.csv',
             *sorted((ROOT / 'extraction/config').rglob('*.yaml')),
             *[ROOT / 'poc/scripts' / name for name in ['build_prompt.py', 'llm_pipeline.py', 'run_pilot.py', 'run_llm_extraction.py']]]
    fingerprint = hashlib.sha256(json.dumps({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                            for p in files}, sort_keys=True).encode()).hexdigest()
    manifest = {'fingerprint': fingerprint, 'model': MODEL, 'project': PROJECT, 'location': 'global',
                'thinking': 'MEDIUM', 'media_resolution': 'MEDIUM', 'budget_usd': args.budget_usd,
                'max_output_tokens': MAX_OUTPUT, 'target_ids': targets,
                'seed_ids': sorted(seed_ids), 'initial_bank_size': len(dataset.bank),
                'example_image_poses': ['id_gridfs_1', 'id_gridfs_3'],
                'ordering': 'round-robin categories, preserving pilot order within each category',
                'input_rate_usd_per_million': .30, 'output_rate_usd_per_million': 2.50,
                'transport_retry_policy': 'up to 2 attempts per product; uncertain attempts retain full reservations',
                'pricing_source': 'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing'}
    old_path = OUT / 'manifest.json'
    if old_path.exists():
        old_manifest = json.loads(old_path.read_text())
        history = old_manifest.get('previous_fingerprints', [])
        if old_manifest['fingerprint'] != fingerprint:
            if not args.accept_code_update:
                raise ValueError('Run fingerprint changed; inspect before mixing versions')
            if old_manifest['target_ids'] != targets or old_manifest['seed_ids'] != sorted(seed_ids):
                raise ValueError('A code update cannot change pilot or seeds')
            write_json(OUT / ('manifest_' + old_manifest['fingerprint'][:12] + '.json'), old_manifest)
            history = history + [old_manifest['fingerprint']]
        manifest['previous_fingerprints'] = history
    if args.execute: write_json(old_path, manifest)
    records = {p.stem: json.loads(p.read_text()) for p in (OUT / 'records').glob('*.json')}
    calls = [json.loads(p.read_text()) for p in (OUT / 'calls').glob('*.json')]
    # Replay in original order so each resumed query sees exactly the accumulated bank.
    for pid in targets:
        if pid in records: dataset.add_reference(records[pid])
    if not args.execute:
        for pid in targets[:args.limit]:
            prompt, neighbors = dataset.prompt(pid)
            body, images = api_body(prompt)
            assert len(images) == len(dataset.images[pid]) + 4
            assert set(body['generationConfig']['responseSchema']['properties']['features']['properties']) == set(requested_rules(dataset.keywords[pid]))
            for part in prompt['parts']:
                if part.get('text', '').startswith(('REFERENCE 1\n', 'REFERENCE 2\n')):
                    assert set(json.loads(part['text'].split('\n', 1)[1])['labels']) == set(requested_rules(dataset.keywords[pid]))
        print('Offline check passed:',args.limit,'targets;',len(dataset.bank),'seed references; no API calls.');return
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id=PROJECT)
    credentials.refresh(Request())
    session = AuthorizedSession(credentials.with_quota_project(PROJECT), max_refresh_attempts=0)
    endpoint = f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}'
    for index, pid in enumerate(targets[:args.limit]):
        if pid in records: continue
        previous = [c for c in calls if c['product_id'] == pid]
        if previous:
            raise RuntimeError(f'Unresolved prior attempt for {pid}; inspect before retrying')
        prompt, neighbors = dataset.prompt(pid);body, images = api_body(prompt)
        write_json(OUT / 'prompts' / (pid + '.json'), prompt)
        # countTokens has no model inference; all billable inference attempts are persisted first.
        counted = session.post(endpoint + ':countTokens', json={
            'contents': body['contents'], 'systemInstruction': body['systemInstruction'],
            'generationConfig': body['generationConfig']}, timeout=60)
        if not counted.ok: raise RuntimeError(f'countTokens HTTP {counted.status_code}: {counted.text[:400]}')
        tokens = counted.json()['totalTokens']
        if tokens > 20000: raise ValueError('Unexpectedly large prompt')
        reservation = (tokens + len(json.dumps(body['generationConfig']['responseSchema']).encode()) + 2048) * INPUT_RATE + MAX_OUTPUT * OUTPUT_RATE
        request_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        result = None
        for attempt in (1, 2):
            spent = sum(c['accounted_usd'] for c in calls)
            if spent + reservation > args.budget_usd:
                checkpoint(dataset, records, seeds, targets, calls)
                raise RuntimeError('Budget limit reached before next inference')
            call = {'call_id': f'pilot_sync/{pid}/{attempt}', 'product_id': pid, 'attempt': attempt,
                    'status': 'reserved', 'accounted_usd': reservation, 'reservation_usd': reservation,
                    'started_at_utc': datetime.now(timezone.utc).isoformat(), 'request_sha256': request_hash,
                    'fingerprint': fingerprint, 'neighbors': neighbors, 'bank_size_before': len(dataset.bank),
                    'images': images, 'input_tokens_counted': tokens}
            calls.append(call); path = OUT / 'calls' / f'{pid}_{attempt}.json';write_json(path, call)
            start = time.monotonic()
            metadata = {'call_id': call['call_id'], 'model': MODEL, 'prompt_fingerprint': fingerprint,
                        'request_sha256': request_hash, 'neighbors': neighbors, 'bank_size_before': len(dataset.bank),
                        'generation_config': body['generationConfig']}
            try:
                response = session.post(endpoint + ':generateContent', json=body, timeout=180)
            except Exception as exc:
                call.update(status='transport_uncertain', error=str(exc)[:500], seconds=time.monotonic()-start)
                write_json(path, call)
                if attempt == 1: time.sleep(5);continue
                result = failure_record(dataset,pid,call['error'],metadata);break
            call.update(http_status=response.status_code, seconds=time.monotonic()-start)
            try: call['response'] = response.json()
            except ValueError: call['response_text'] = response.text[:2000]
            write_json(path, call)
            if not response.ok:
                call.update(status='http_error', error=f'HTTP {response.status_code}')
                write_json(path,call)
                if response.status_code in (429,500,502,503,504) and attempt == 1:
                    time.sleep(10);continue
                result = failure_record(dataset,pid,f'HTTP {response.status_code}',metadata)
                if response.status_code in (400,401,403,404):
                    # A request/config/auth error must not repeat across the whole dataset.
                    write_json(OUT / 'records' / (pid+'.json'), result);records[pid]=result
                    checkpoint(dataset, records, seeds, targets, calls)
                    raise RuntimeError(f'Systematic API error: HTTP {response.status_code}: {response.text[:600]}')
                break
            try:
                data = call['response'];usage = data['usageMetadata']
                if 'promptTokenCount' not in usage or 'candidatesTokenCount' not in usage:
                    raise ValueError('Missing usage; retaining reservation')
                cost = usage['promptTokenCount']*INPUT_RATE + (usage['candidatesTokenCount']+usage.get('thoughtsTokenCount',0))*OUTPUT_RATE
                call.update(usage=usage, estimated_usd=cost, accounted_usd=cost)
                metadata.update(usage=usage,estimated_usd=cost)
                candidate = data['candidates'][0]
                if candidate.get('finishReason') != 'STOP': raise ValueError('Incomplete/blocked model response')
                text=''.join(p.get('text','') for p in candidate['content']['parts'] if not p.get('thought'))
                parsed=json.loads(text);call['parsed_output']=parsed
                result=dataset.result(pid,parsed,metadata)
                call.update(status='completed',result_status=result['status'])
            except Exception as exc:
                call.update(status='validation_error',error=str(exc)[:800])
                result=failure_record(dataset,pid,call['error'],metadata)
            write_json(path,call);break
        result['annotation_origin'] = 'llm'
        write_json(OUT / 'records' / (pid+'.json'),result);records[pid]=result;dataset.add_reference(result)
        total=sum(c['accounted_usd'] for c in calls)
        progress={'processed':len(records),'planned':len(targets),'last_product_id':pid,'last_status':result['status'],
                  'bank_size':len(dataset.bank),'accounted_usd':total,'updated_at_utc':datetime.now(timezone.utc).isoformat()}
        write_json(OUT/'progress.json',progress)
        print(f"{len(records)}/{len(targets)} {dataset.keywords[pid]['category']} {pid} {result['status']} bank={len(dataset.bank)} cost=${total:.6f}",flush=True)
        if len(records)%20==0:checkpoint(dataset,records,seeds,targets,calls)
        # Stop repeated failures rather than spend on a systemic issue.
        recent=[records[p]['product_status']=='processing_error' for p in targets[:index+1] if p in records][-5:]
        if len(recent)==5 and all(recent):
            checkpoint(dataset,records,seeds,targets,calls);raise RuntimeError('Five consecutive processing errors; stopped')
    summary=checkpoint(dataset,records,seeds,targets,calls,complete=len(records)==len(targets))
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
