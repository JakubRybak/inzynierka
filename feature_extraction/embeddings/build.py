"""Build independent image/description vectors with resumable spending guards."""
import argparse
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import fcntl
import json
from pathlib import Path
import signal
import threading
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from ..data import load_inputs
from ..settings import load_settings, validate_embedding_settings
from ..storage import digest, write_json
from .client import EmbeddingClient, EmbeddingRejected


RATE_LIMIT_DELAYS = (2.0, 4.0, 8.0, 16.0, 32.0)


def log_event(message):
    print(f'[embeddings] {message}', flush=True)


def pause_for(seconds):
    if seconds > 0:
        time.sleep(seconds)


def rate_limit_delay(retry_number, retry_after=None):
    if retry_after is not None and retry_after > 0:
        return float(retry_after)
    index = min(max(retry_number - 1, 0), len(RATE_LIMIT_DELAYS) - 1)
    return RATE_LIMIT_DELAYS[index]


def inputs_for(catalog):
    ids, source, images, references, _, _ = catalog
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


def build(settings, limit=None, execute=False, *, catalog=None, export_folder=None):
    folder = Path(settings['embeddings'])
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / '.run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if catalog is None:
            catalog = load_inputs(settings, limit)
        return encode(settings, folder, inputs_for(catalog), execute, export_folder)


def write_ledger(path, ledger, serialized_lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    if serialized_lines:
        temporary.write_text('[\n' + ',\n'.join(serialized_lines) + '\n]\n')
    else:
        temporary.write_text('[]\n')
    temporary.replace(path)


def validate_cached_vector(cached, dimension, pid):
    vector = np.asarray(cached['values'], dtype=np.float32)
    if vector.shape != (dimension,) or not np.isfinite(vector).all() or np.linalg.norm(vector) <= 0:
        raise ValueError(f'Invalid cached embedding for {pid}')
    vector /= np.linalg.norm(vector)
    return vector.tolist()


def encode(settings, folder, inputs, execute, export_folder):
    cfg = validate_embedding_settings(settings['embedding_api'])
    # Match the previous cache identity when using the same model and input recipe.
    recipe = {'project': settings['api']['project'], 'model': cfg['model'], 'location': settings['api']['location'],
              'output_dimensionality': cfg['dimension'], 'task_type': None,
              'text_input': 'description only, verbatim, no instruction prefix',
              'image_input': 'first source CSV image, original PNG bytes',
              'normalization': 'L2 float32 before Parquet export'}
    fingerprint = digest(json.dumps(recipe, sort_keys=True).encode())
    ledger_path = folder / 'cost_ledger.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    uncertain_keys = {(r['product_id'], r['modality']) for r in ledger if r['status'] != 'rejected'}
    normalized_by_key = {}
    pending_tasks = deque()
    missing = 0

    for item in inputs:
        pid, modality = item['product_id'], item['modality']
        path = folder / 'cache' / modality / f'{pid}.json'
        if path.exists():
            cached = json.loads(path.read_text())
            if cached['settings_sha256'] != fingerprint or cached['input_sha256'] != item['input_sha256']:
                raise ValueError(f'Stale embedding cache for {pid}/{modality}; choose a new embedding folder')
            normalized_by_key[(pid, modality)] = validate_cached_vector(cached, cfg['dimension'], pid)
        else:
            missing += 1
            if not execute:
                continue
            if (pid, modality) in uncertain_keys:
                raise RuntimeError(f'Prior uncertain embedding for {pid}/{modality}; inspect ledger before paying again')
            pending_tasks.append({
                'item': item,
                'path': path,
                'rate_limit_retries': 0,
                'auth_retries': 0,
                'needs_refresh': False,
            })

    if execute and pending_tasks:
        run_online_embeddings(settings['api'], cfg, fingerprint, ledger_path, ledger, pending_tasks, normalized_by_key)

    rows = {'image': [], 'text': []}
    for item in inputs:
        pid, modality = item['product_id'], item['modality']
        vector = normalized_by_key.get((pid, modality))
        if vector is None:
            continue
        row = {'product_id': pid, 'embedding': vector, 'input_sha256': item['input_sha256']}
        if modality == 'image':
            row.update(image_id=item['image_id'], image_path=item['image_path'])
        rows[modality].append(row)

    summary = {'selected_products_including_references': len(inputs) // 2, 'missing_vectors_before_run': missing,
               'cached_vectors': {m: len(r) for m, r in rows.items()}, 'execute': execute}
    if execute or (export_folder is not None and missing == 0):
        export = Path(export_folder) if export_folder is not None else folder
        export.mkdir(parents=True, exist_ok=True)
        expected = len(inputs) // 2
        # Reject subset exports over an existing larger export.
        old_path = export / 'manifest.json'
        if old_path.exists():
            old = json.loads(old_path.read_text())
            if old.get('expected_per_modality', expected) > expected:
                raise ValueError('Refusing to replace a larger embedding export with a subset')
        for modality, values in rows.items():
            fields = [('product_id', pa.string()), ('embedding', pa.list_(pa.float32(), cfg['dimension'])),
                      ('input_sha256', pa.string())]
            if modality == 'image':
                fields += [('image_id', pa.string()), ('image_path', pa.string())]
            temporary = export / f'{modality}.parquet.tmp'
            pq.write_table(pa.Table.from_pylist(values, schema=pa.schema(fields)), temporary, compression='zstd')
            temporary.replace(export / f'{modality}.parquet')
        write_json(old_path, {**recipe, 'settings_sha256': fingerprint, 'expected_per_modality': expected,
                              'counts': {m: len(r) for m, r in rows.items()},
                              'complete': all(len(r) == expected for r in rows.values()),
                              'estimated_cost_usd': sum(r['accounted_usd'] for r in ledger)})
    return summary


def run_online_embeddings(api_cfg, cfg, fingerprint, ledger_path, ledger, pending_tasks, normalized_by_key):
    active_limit = cfg['concurrency']
    max_rate_retries = cfg['max_rate_limit_retries']
    max_auth_retries = cfg['max_auth_retries']
    reduction_epoch = 0
    pause_until = 0.0
    auth_epoch = 0
    auth_lock = threading.Lock()
    thread_local = threading.local()
    total_missing = len(pending_tasks)
    completed_this_run = 0
    accounted_total = sum(r['accounted_usd'] for r in ledger)
    serialized_ledger = [json.dumps(r, ensure_ascii=False) for r in ledger]

    stop_signal = None
    terminal_error = None
    stop_reason = None

    def worker_call(content, modality, target_auth_epoch):
        nonlocal auth_epoch
        client = getattr(thread_local, 'client', None)
        if client is None:
            client = EmbeddingClient(api_cfg, cfg)
            thread_local.client = client
            thread_local.auth_epoch = auth_epoch
        if target_auth_epoch is not None:
            with auth_lock:
                if auth_epoch < target_auth_epoch:
                    client.refresh()
                    auth_epoch = target_auth_epoch
                    thread_local.auth_epoch = auth_epoch
        if getattr(thread_local, 'auth_epoch', -1) < auth_epoch:
            client.refresh()
            thread_local.auth_epoch = auth_epoch
        return client.encode(content, modality)

    previous_handlers = {}
    can_install_signals = threading.current_thread() is threading.main_thread()

    def handle_signal(signum, _frame):
        nonlocal stop_signal, stop_reason
        if stop_signal is None:
            stop_signal = signum
            sig_name = signal.Signals(signum).name if signum in signal.Signals._value2member_map_ else str(signum)
            stop_reason = f'signal {sig_name}'
            log_event(f'Received {sig_name}; stopping new requests and finishing in-flight calls')

    if can_install_signals:
        for sig in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, handle_signal)

    in_flight = {}
    try:
        with ThreadPoolExecutor(max_workers=cfg['concurrency']) as executor:
            while pending_tasks or in_flight:
                while (stop_signal is None and terminal_error is None
                       and pending_tasks and len(in_flight) < active_limit):
                    now = time.monotonic()
                    if now < pause_until:
                        if in_flight:
                            break
                        sleep_for = pause_until - now
                        if sleep_for > 0:
                            pause_for(sleep_for)
                        continue

                    task = pending_tasks[0]
                    item = task['item']
                    pid, modality = item['product_id'], item['modality']
                    rate = cfg[f'{modality}_usd_per_million'] / 1_000_000
                    reservation = cfg['max_input_tokens'] * rate
                    if accounted_total + reservation > cfg['budget_usd']:
                        pending_tasks.popleft()
                        terminal_error = RuntimeError('Persistent embedding budget guard reached')
                        stop_reason = 'budget guard reached'
                        log_event('Stopping embedding run: persistent embedding budget guard reached')
                        break

                    pending_tasks.popleft()
                    entry = {'product_id': pid, 'modality': modality, 'status': 'reserved',
                             'settings_sha256': fingerprint, 'input_sha256': item['input_sha256'],
                             'accounted_usd': reservation}
                    entry_idx = len(ledger)
                    ledger.append(entry)
                    serialized_ledger.append(json.dumps(entry, ensure_ascii=False))
                    accounted_total += reservation
                    write_ledger(ledger_path, ledger, serialized_ledger)
                    target_auth = (auth_epoch + 1) if task.pop('needs_refresh', False) else None
                    future = executor.submit(worker_call, item['content'], modality, target_auth)
                    in_flight[future] = (task, entry, entry_idx, reservation, rate, reduction_epoch)

                if not in_flight:
                    break

                timeout = None
                if (stop_signal is None and terminal_error is None
                        and pending_tasks and len(in_flight) < active_limit and pause_until > time.monotonic()):
                    timeout = max(0.0, pause_until - time.monotonic())

                done, _ = wait(list(in_flight), timeout=timeout, return_when=FIRST_COMPLETED)
                for future in done:
                    task, entry, entry_idx, reservation, rate, sent_epoch = in_flight.pop(future)
                    item = task['item']
                    pid, modality = item['product_id'], item['modality']
                    try:
                        data = future.result()
                        values = data['embedding']['values']
                        tokens = data['usageMetadata']['promptTokenCount']
                        vector = np.asarray(values, dtype=np.float32)
                        if (vector.shape != (cfg['dimension'],) or not np.isfinite(vector).all()
                                or np.linalg.norm(vector) <= 0 or data.get('truncated')
                                or not 0 < tokens <= cfg['max_input_tokens']):
                            raise ValueError('Invalid embedding response or usage')
                        cached = {'settings_sha256': fingerprint, 'input_sha256': item['input_sha256'],
                                  'values': values, 'usage': data['usageMetadata']}
                        write_json(task['path'], cached)
                        actual_cost = tokens * rate
                        entry.update(status='completed', input_tokens=tokens, accounted_usd=actual_cost)
                        serialized_ledger[entry_idx] = json.dumps(entry, ensure_ascii=False)
                        accounted_total += actual_cost - reservation
                        write_ledger(ledger_path, ledger, serialized_ledger)
                        normalized_by_key[(pid, modality)] = (vector / np.linalg.norm(vector)).tolist()
                        completed_this_run += 1
                        if completed_this_run % 250 == 0 or completed_this_run == total_missing:
                            log_event(f'Progress: {completed_this_run}/{total_missing} missing vectors saved '
                                      f'(concurrency={active_limit}, accounted_usd=${accounted_total:.4f})')
                    except EmbeddingRejected as error:
                        entry.update(status='rejected', error=str(error), accounted_usd=0)
                        serialized_ledger[entry_idx] = json.dumps(entry, ensure_ascii=False)
                        accounted_total -= reservation
                        write_ledger(ledger_path, ledger, serialized_ledger)
                        status_code = getattr(error, 'status_code', None)
                        if status_code is None:
                            if 'HTTP 429' in str(error):
                                status_code = 429
                            elif 'HTTP 401' in str(error):
                                status_code = 401

                        if status_code == 429:
                            if sent_epoch == reduction_epoch:
                                old_limit = active_limit
                                active_limit = max(1, active_limit - 1)
                                reduction_epoch += 1
                                if active_limit < old_limit:
                                    log_event(f'HTTP 429 for {pid}/{modality}: reducing concurrency {old_limit} -> {active_limit}')
                                else:
                                    log_event(f'HTTP 429 for {pid}/{modality}: concurrency stays at {active_limit}')
                            if stop_signal is None and terminal_error is None:
                                if task['rate_limit_retries'] < max_rate_retries:
                                    task['rate_limit_retries'] += 1
                                    delay = rate_limit_delay(task['rate_limit_retries'], getattr(error, 'retry_after', None))
                                    now = time.monotonic()
                                    pause_until = max(pause_until, now + delay)
                                    effective_wait = max(0.0, pause_until - now)
                                    log_event(f'HTTP 429 retry {task["rate_limit_retries"]}/{max_rate_retries} '
                                              f'for {pid}/{modality}; shared pause {effective_wait:.1f}s')
                                    pending_tasks.appendleft(task)
                                else:
                                    msg = (f'Rate limit retries exhausted ({max_rate_retries} retries) '
                                           f'for {pid}/{modality}: {error}')
                                    terminal_error = EmbeddingRejected(msg, status_code=429)
                                    stop_reason = f'rate limit retries exhausted for {pid}/{modality}'
                                    log_event(f'Stopping embedding run: {stop_reason}')
                        elif status_code == 401:
                            if stop_signal is None and terminal_error is None:
                                if task['auth_retries'] < max_auth_retries:
                                    task['auth_retries'] += 1
                                    task['needs_refresh'] = True
                                    log_event(f'HTTP 401 for {pid}/{modality}: refreshing token and retrying '
                                              f'({task["auth_retries"]}/{max_auth_retries})')
                                    pending_tasks.appendleft(task)
                                else:
                                    msg = (f'Authentication retries exhausted ({max_auth_retries} retries) '
                                           f'for {pid}/{modality}: {error}')
                                    terminal_error = EmbeddingRejected(msg, status_code=401)
                                    stop_reason = f'auth retries exhausted for {pid}/{modality}'
                                    log_event(f'Stopping embedding run: {stop_reason}')
                        else:
                            if terminal_error is None:
                                terminal_error = error
                                stop_reason = f'rejected request for {pid}/{modality} ({error})'
                                log_event(f'Stopping embedding run: {stop_reason}')
                    except Exception as error:
                        entry.update(status='failed_or_uncertain', error=str(error))
                        serialized_ledger[entry_idx] = json.dumps(entry, ensure_ascii=False)
                        write_ledger(ledger_path, ledger, serialized_ledger)
                        if terminal_error is None:
                            terminal_error = error
                            stop_reason = f'uncertain or failed call for {pid}/{modality} ({error})'
                            log_event(f'Stopping embedding run: {stop_reason}')
    finally:
        if can_install_signals:
            for sig, handler in previous_handlers.items():
                signal.signal(sig, handler)

    if stop_signal is not None:
        log_event(f'Embedding run finished early due to {stop_reason}')
        raise KeyboardInterrupt(f'Embedding run stopped by {stop_reason}')
    if terminal_error is not None:
        log_event(f'Embedding run finished with error: {stop_reason}')
        raise terminal_error
    log_event('Embedding run completed all missing vectors')


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
