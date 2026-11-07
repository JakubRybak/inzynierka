"""Extract features with isolated, resumable online and batch runs."""
import fcntl
import json
from collections import Counter
from pathlib import Path

from .data import load_inputs
from .keywords.engine import extract_product
from .validation import validate
from .llm.batch import BatchClient
from .llm.client import APIError, ExtractionClient
from .llm.prompt_builder import build_prompt
from .llm.references import ReferenceBank
from .llm.validation import merge_result
from .settings import BASE, validate_batch_settings
from .storage import digest, export_products, read_jsonl, write_json, write_jsonl


def uniform(record, origin):
    columns = ['product_id', 'brand', 'section', 'category', 'features', 'feature_metadata', 'status', 'exclusion_reasons']
    return {**{key: record[key] for key in columns}, 'product_status': record.get('product_status', 'ok'),
            'product_reason': record.get('product_reason', ''),
            'outside_schema_reasons': record.get('outside_schema_reasons', {}),
            'llm_metadata': record.get('llm_metadata', {}), 'annotation_origin': origin}


def run(settings, run_name, stage='all', execute=False, limit=None, mode='online', batch_size=None):
    if mode not in {'online', 'batch'}:
        raise ValueError(f'Unknown extraction mode: {mode}')
    if batch_size is not None and (mode != 'batch' or batch_size < 1):
        raise ValueError('batch_size must be positive and requires batch mode')
    if mode == 'batch':
        if stage == 'keywords':
            raise ValueError('Batch mode requires the LLM stage')
        validate_batch_settings(settings)
    if not run_name.replace('_', '').replace('-', '').isalnum():
        raise ValueError('Run name must contain letters, digits, underscores or hyphens')
    folder = Path(settings['artifacts']) / 'runs' / run_name
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / '.run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return extract(settings, folder, stage, execute, limit, mode, batch_size)


def extract(settings, folder, stage, execute, limit, mode, batch_size):
    ids, source, images, seeds, configs, schemas = load_inputs(settings, limit)
    keywords = {pid: extract_product(source[pid], configs[(source[pid]['section'], source[pid]['category'])],
                                     schemas[(source[pid]['section'], source[pid]['category'])])
                for pid in ids}
    validate(list(keywords.values()), schemas)
    # Hash all source evidence and code that can change prompt selection or output.
    evidence_ids = set(ids) | {r['product_id'] for r in seeds}
    files = sorted(BASE.rglob('*.py')) + sorted((BASE / 'llm/prompts').glob('*.txt'))
    files += sorted((BASE / 'llm/prompts').rglob('*.json')) + sorted((BASE / 'keywords/definitions').rglob('*.yaml'))
    files += sorted((BASE / 'schema').rglob('*.yaml'))
    provenance = {'settings': settings, 'ids': ids, 'references': seeds,
                  'source': {pid: source[pid] for pid in sorted(evidence_ids)},
                  'images': {pid: [{**r, 'sha256': digest(Path(r['path']).read_bytes())} for r in images.get(pid, [])]
                             for pid in sorted(evidence_ids)},
                  'code': {str(p.relative_to(BASE)): digest(p.read_bytes()) for p in files}}
    if Path(settings['embeddings']).joinpath('manifest.json').exists():
        provenance['embeddings'] = {name: digest((Path(settings['embeddings']) / name).read_bytes())
                                    for name in ['manifest.json', 'image.parquet', 'text.parquet']}
    if mode == 'batch':
        # Budget and poll interval can be adjusted while resuming the same job.
        batch_settings = {k: v for k, v in settings['batch'].items() if k not in {'budget_usd', 'poll_seconds'}}
        provenance['settings'] = {**settings, 'batch': batch_settings}
        provenance['batch_size'] = batch_size
        provenance['mode'] = mode
    else:
        provenance['settings'] = {k: v for k, v in settings.items() if k != 'batch'}
    fingerprint = digest(json.dumps(provenance, sort_keys=True).encode())
    snapshot = folder / 'config.json'
    if snapshot.exists() and json.loads(snapshot.read_text())['fingerprint'] != fingerprint:
        raise ValueError('Run inputs/configuration changed; choose a new run name')
    write_json(snapshot, {'fingerprint': fingerprint, 'settings': settings, 'product_ids': ids,
                          'mode': mode, 'batch_size': batch_size})
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
    if mode == 'batch':
        return extract_batches(settings, folder, ids, source, images, keywords, records, bank, seed_map,
                               fingerprint, execute, batch_size)
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
            prompt, context = prepare_request(original, source, images, bank, settings['api'], fingerprint)
            write_json(folder / 'requests' / f'{pid}_prompt.json', prompt)
            planned += 1
            if not execute:
                continue
            parsed, metadata = client.generate(pid, prompt, context)
            record = apply_response(original, parsed, metadata)
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


def prepare_request(record, source, images, bank, api, fingerprint):
    pid = record['product_id']
    examples, neighbors = bank.examples(record)
    prompt = build_prompt(record, source[pid], [r['path'] for r in images[pid]], examples)
    prompt['generation_config'].update(thinkingConfig={'thinkingLevel': api['thinking_level']},
                                       mediaResolution=api['media_resolution'])
    if 'temperature' in api:
        prompt['generation_config']['temperature'] = api['temperature']
    context = {'neighbors': neighbors, 'bank_size_before': len(bank.bank),
               'prompt_fingerprint': fingerprint}
    return prompt, context


def apply_response(original, parsed, metadata, error=''):
    if not error:
        try:
            record = merge_result(original, parsed, metadata)
            fields = ('call_id', 'model', 'neighbors', 'bank_size_before', 'prompt_fingerprint',
                      'generation_config', 'usage', 'estimated_usd', 'batch_job')
            record['llm_metadata'] = {key: metadata[key] for key in fields if key in metadata}
            return record
        except (ValueError, KeyError, TypeError) as exc:
            error = str(exc)
    record = uniform(original, 'llm')
    record.update(status='needs_review', product_status='processing_error', product_reason=error,
                  llm_metadata={key: metadata[key] for key in ('call_id', 'model', 'batch_job')
                                if key in metadata})
    return record


def extract_batches(settings, folder, ids, source, images, keywords, records, bank, seeds,
                    fingerprint, execute, batch_size):
    client = BatchClient(settings['api'], settings['batch'], folder / 'batch', fingerprint)
    for pid in ids:
        if pid not in records:
            original = keywords[pid]
            if original['status'] in {'excluded', 'ready'}:
                records[pid] = uniform(original, 'keywords')
            elif pid in seeds:
                records[pid] = uniform(seeds[pid], 'manual')
        if pid in records:
            bank.add(records[pid])

    def save_progress():
        export_products(folder, (records[pid] for pid in ids if pid in records))
        write_jsonl(folder / 'reference_bank.jsonl', bank.bank.values())

    manifests = sorted(client.folder.glob('*/manifest.json'))
    completed = 0
    planned = 0
    reservation = 0
    active_batch = None
    retry_ids = set()
    save_progress()
    try:
        # Revisit a saved manifest before preparing new prompts.
        number = 1
        while number <= len(manifests) or len(records) < len(ids):
            batch_folder = client.folder / f'{number:06d}'
            if number <= len(manifests):
                manifest = json.loads(manifests[number - 1].read_text())
            else:
                retry_ids.difference_update(records)
                pending = [pid for pid in ids if pid not in records and (not retry_ids or pid in retry_ids)]
                pending = pending[:batch_size]
                prompts = ((pid, *prepare_request(keywords[pid], source, images, bank,
                                                 settings['api'], fingerprint)) for pid in pending)
                manifest = client.prepare(batch_folder, prompts)
            missing = {entry['product_id'] for entry in manifest['entries'].values()} - records.keys()
            if not missing:
                completed += 1
                number += 1
                continue
            state_path = batch_folder / 'job.json'
            if state_path.exists():
                saved = json.loads(state_path.read_text())
                if saved.get('retry_missing') and missing <= set(saved['missing_product_ids']):
                    # All available rows were saved. Retry the missing products before moving on.
                    retry_ids.update(missing)
                    number += 1
                    continue
            active_batch = batch_folder.name
            planned = len(manifest['entries'])
            reservation = manifest['reservation_usd']
            if not execute:
                break
            state = client.start(batch_folder, manifest)
            job = client.wait(batch_folder, state)
            results = {pid: apply_response(keywords[pid], parsed, metadata, error)
                       for pid, parsed, metadata, error in client.collect(batch_folder, manifest, state, job)}
            # Publish the returned rows before allowing the bank to inform new prompts.
            for record in results.values():
                bank.add(record)
            records.update(results)
            save_progress()
            missing -= results.keys()
            if missing:
                planned = len(missing)
                raise APIError(f'Batch {batch_folder.name} returned no result for {planned} products. '
                               'Available results were saved. Run the same command to resume')
            completed += 1
            number += 1
            active_batch = None
            planned = 0
            reservation = 0
    finally:
        summary = {'mode': 'batch', 'execute': execute, 'selected': len(ids), 'saved': len(records),
                   'complete': len(records) == len(ids), 'batches_completed': completed,
                   'active_batch': active_batch, 'planned_calls': planned, 'reservation_usd': reservation,
                   'statuses': dict(Counter(r['status'] for r in records.values())),
                   'bank_size': len(bank.bank), 'accounted_usd': client.spent()}
        write_json(folder / 'summary.json', summary)
    return summary
