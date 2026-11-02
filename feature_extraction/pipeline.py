"""Sequential extraction with isolated runs, durable requests and resumable results."""
import fcntl
import json
from collections import Counter
from pathlib import Path

from .data import load_inputs
from .keywords.engine import extract_product
from .keywords.validation import validate
from .llm.client import ExtractionClient
from .llm.prompt_builder import build_prompt, requested_rules
from .llm.references import ReferenceBank
from .llm.validation import merge_result
from .settings import BASE
from .storage import digest, export_products, read_jsonl, write_json, write_jsonl


def uniform(record, origin):
    columns = ['product_id', 'brand', 'section', 'category', 'features', 'feature_metadata', 'status', 'exclusion_reasons']
    return {**{key: record[key] for key in columns}, 'product_status': record.get('product_status', 'ok'),
            'product_reason': record.get('product_reason', ''),
            'outside_schema_reasons': record.get('outside_schema_reasons', {}),
            'llm_metadata': record.get('llm_metadata', {}), 'annotation_origin': origin}


def run(settings, run_name, stage='all', execute=False, limit=None):
    if not run_name.replace('_', '').replace('-', '').isalnum():
        raise ValueError('Run name must contain letters, digits, underscores or hyphens')
    folder = Path(settings['artifacts']) / 'runs' / run_name
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / '.run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return extract(settings, folder, stage, execute, limit)


def extract(settings, folder, stage, execute, limit):
    ids, source, images, seeds, configs = load_inputs(settings, limit)
    keywords = {pid: extract_product(source[pid], configs[(source[pid]['section'], source[pid]['category'])])
                for pid in ids}
    validate(list(keywords.values()), configs)
    # Hash all source evidence and code that can change prompt selection or output.
    evidence_ids = set(ids) | {r['product_id'] for r in seeds}
    files = sorted(BASE.rglob('*.py')) + sorted((BASE / 'llm/prompts').glob('*.txt'))
    files += sorted((BASE / 'llm/prompts').glob('*.json')) + sorted((BASE / 'keywords/definitions').rglob('*.yaml'))
    provenance = {'settings': settings, 'ids': ids, 'references': seeds,
                  'source': {pid: source[pid] for pid in sorted(evidence_ids)},
                  'images': {pid: [{**r, 'sha256': digest(Path(r['path']).read_bytes())} for r in images.get(pid, [])]
                             for pid in sorted(evidence_ids)},
                  'code': {str(p.relative_to(BASE)): digest(p.read_bytes()) for p in files}}
    if Path(settings['embeddings']).joinpath('manifest.json').exists():
        provenance['embeddings'] = {name: digest((Path(settings['embeddings']) / name).read_bytes())
                                    for name in ['manifest.json', 'image.parquet', 'text.parquet']}
    fingerprint = digest(json.dumps(provenance, sort_keys=True).encode())
    snapshot = folder / 'config.json'
    if snapshot.exists() and json.loads(snapshot.read_text())['fingerprint'] != fingerprint:
        raise ValueError('Run inputs/configuration changed; choose a new run name')
    write_json(snapshot, {'fingerprint': fingerprint, 'settings': settings, 'product_ids': ids})
    write_jsonl(folder / 'keywords.jsonl', keywords.values())
    records = {r['product_id']: r for r in read_jsonl(folder / 'products.jsonl')
               if r.get('annotation_origin') != 'keywords' or r['status'] != 'pending'}
    if stage == 'keywords':
        results = [uniform(keywords[pid], 'keywords') for pid in ids]
        export_products(folder, results)
        summary = {'stage': stage, 'products': len(results), 'statuses': dict(Counter(r['status'] for r in results))}
        write_json(folder / 'summary.json', summary)
        return summary
    bank = ReferenceBank(seeds, source, images, settings['embeddings'], ids)
    seed_map = {r['product_id']: r for r in seeds}
    client = ExtractionClient(settings['api'], folder / 'requests') if execute else None
    planned = 0
    try:
        for pid in ids:
            if pid in records:
                bank.add(records[pid])
                continue
            original = keywords[pid]
            if original['status'] in {'excluded', 'ready'}:
                records[pid] = uniform(original, 'keywords')
                if original['status'] == 'ready':
                    bank.add(records[pid])
                continue
            if pid in seed_map:
                records[pid] = uniform(seed_map[pid], 'manual')
                continue
            examples, neighbors = bank.examples(original)
            prompt = build_prompt(original, source[pid], [r['path'] for r in images[pid]], examples)
            cfg = settings['api']
            prompt['generation_config'].update(thinkingConfig={'thinkingLevel': cfg['thinking_level']},
                                              mediaResolution=cfg['media_resolution'])
            if 'temperature' in cfg:
                prompt['generation_config']['temperature'] = cfg['temperature']
            write_json(folder / 'requests' / f'{pid}_prompt.json', prompt)
            planned += 1
            if not execute:
                continue
            parsed, metadata = client.generate(pid, prompt, {'neighbors': neighbors, 'bank_size_before': len(bank.bank),
                                                            'prompt_fingerprint': fingerprint})
            try:
                record = merge_result(original, parsed, metadata)
                # Store references and accounting once, without duplicating raw response data in products.
                record['llm_metadata'] = {k: metadata[k] for k in ['call_id', 'model', 'neighbors', 'bank_size_before',
                                                                 'prompt_fingerprint', 'generation_config', 'usage', 'estimated_usd']}
            except (ValueError, KeyError) as error:
                record = uniform(original, 'llm')
                record.update(status='needs_review', product_status='processing_error', product_reason=str(error),
                              llm_metadata={'call_id': metadata['call_id'], 'model': metadata['model']})
            records[pid] = record
            bank.add(record)
            export_products(folder, [records[p] for p in ids if p in records])
            write_jsonl(folder / 'reference_bank.jsonl', bank.bank.values())
            print(f'{len(records)}/{len(ids)} {pid} {record["status"]}', flush=True)
    finally:
        export_products(folder, [records[p] for p in ids if p in records])
        write_jsonl(folder / 'reference_bank.jsonl', bank.bank.values())
        summary = {'stage': stage, 'execute': execute, 'selected': len(ids), 'saved': len(records),
                   'planned_calls_this_invocation': planned, 'complete': execute and len(records) == len(ids),
                   'statuses': dict(Counter(r['status'] for r in records.values())),
                   'bank_size': len(bank.bank), 'accounted_usd': client.spent() if client else 0}
        write_json(folder / 'summary.json', summary)
    return summary
