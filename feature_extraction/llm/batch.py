"""Submit and recover Vertex Gemini batch jobs backed by Cloud Storage."""
from concurrent.futures import ThreadPoolExecutor
import json
import threading
import time
from pathlib import Path
from urllib.parse import quote

from ..storage import digest, write_json, write_jsonl
from .client import APIError, REJECTED_HTTP_STATUSES, VertexSession
from .request import estimated_cost, parse_response, request_body

TERMINAL_STATES = {
    'JOB_STATE_SUCCEEDED', 'JOB_STATE_PARTIALLY_SUCCEEDED', 'JOB_STATE_FAILED',
    'JOB_STATE_CANCELLED', 'JOB_STATE_EXPIRED', 'JOB_STATE_PAUSED',
}
RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}
UPLOAD_WORKERS = 8


def request_key(request):
    # Vertex echoes request contents, with null fields added to some parts.
    contents = [{**content, 'parts': [{key: value for key, value in part.items() if value is not None}
                                      for part in content['parts']]}
                for content in request['contents']]
    return digest(json.dumps(contents, sort_keys=True).encode())


class BatchClient:
    def __init__(self, api, config, folder, fingerprint):
        self.api, self.config, self.folder = api, config, Path(folder)
        self.bucket = config['bucket']
        self.prefix = f'{config["prefix"].strip("/")}/{self.folder.parent.name}-{fingerprint[:24]}'
        self.rates = {key: config[key] for key in ('input_usd_per_million', 'output_usd_per_million')}
        self.transport = None
        self.uploaded = set()
        self._upload_lock = threading.Lock()
        self._auth_lock = threading.Lock()
        self._auth_epoch = 0
        self._thread_local = threading.local()
        self.per_request = estimated_cost({'promptTokenCount': api['max_input_tokens'],
                                           'candidatesTokenCount': api['max_output_tokens']}, self.rates)

    def uri(self, name):
        return f'gs://{self.bucket}/{name}'

    def prepare(self, folder, prompts):
        entries, requests, images = {}, [], {}

        def image_uri(sha, mime, path):
            # Separate products can share identical bytes. Keep distinct paths for matching.
            name = f'{self.prefix}/images/{digest(str(path).encode())[:24]}-{sha}'
            images[name] = {'path': str(path), 'sha256': sha, 'mime': mime}
            return self.uri(name)

        for product_id, prompt, context in prompts:
            request, _ = request_body(prompt, self.api['max_output_tokens'], image_uri)
            key = request_key(request)
            if key in entries:
                raise ValueError(f'Indistinguishable batch request for {product_id}')
            entries[key] = {'product_id': product_id, 'generation_config': request['generationConfig'], **context}
            requests.append({'request': request})
        write_jsonl(folder / 'input.jsonl', requests)
        manifest = {'entries': entries, 'images': images, 'reservation_usd': self.per_request * len(entries),
                    'input_sha256': digest((folder / 'input.jsonl').read_bytes())}
        write_json(folder / 'manifest.json', manifest)
        return manifest

    def spent(self):
        return sum(json.loads(path.read_text())['accounted_usd'] for path in self.folder.glob('*/job.json'))

    def _refresh_transport(self, transport, expected_epoch):
        with self._auth_lock:
            if self._auth_epoch == expected_epoch:
                if hasattr(transport, 'refresh'):
                    transport.refresh()
                if self.transport is not None and self.transport is not transport and hasattr(self.transport, 'refresh'):
                    self.transport.refresh()
                self._auth_epoch += 1

    def request(self, method, url, **kwargs):
        if self.transport is None:
            self.transport = VertexSession(self.api)
        auth_retries = 0
        while True:
            epoch = self._auth_epoch
            response = self.transport.session.request(method, url, timeout=self.api['timeout_seconds'], **kwargs)
            if getattr(response, 'status_code', None) == 401 and auth_retries < 2 and hasattr(self.transport, 'refresh'):
                auth_retries += 1
                self._refresh_transport(self.transport, epoch)
                continue
            return response

    def _retryable_request(self, method, url, *, session_transport=None, **kwargs):
        auth_retries = 0
        transient_retries = 0
        while True:
            epoch = self._auth_epoch
            try:
                if session_transport is None:
                    response = self.request(method, url, **kwargs)
                else:
                    if getattr(self._thread_local, 'auth_epoch', -1) < epoch and hasattr(session_transport, 'refresh'):
                        session_transport.refresh()
                        self._thread_local.auth_epoch = epoch
                    response = session_transport.session.request(
                        method, url, timeout=self.api['timeout_seconds'], **kwargs)
            except (ConnectionError, OSError) as exc:
                if isinstance(exc, TimeoutError) or transient_retries >= 4:
                    raise
                transient_retries += 1
                time.sleep(min(2 ** transient_retries, 16))
                continue

            status = getattr(response, 'status_code', None)
            if status == 401 and auth_retries < 2 and session_transport is not None and hasattr(session_transport, 'refresh'):
                auth_retries += 1
                self._refresh_transport(session_transport, epoch)
                self._thread_local.auth_epoch = self._auth_epoch
                continue
            if status in RETRYABLE_HTTP_STATUSES and transient_retries < 4:
                transient_retries += 1
                time.sleep(min(2 ** transient_retries, 16))
                continue
            return response

    def _upload_with_transport(self, transport, name, data, mime):
        with self._upload_lock:
            if name in self.uploaded:
                return
        url = f'https://storage.googleapis.com/upload/storage/v1/b/{self.bucket}/o'
        response = self._retryable_request(
            'POST', url, session_transport=transport, data=data, headers={'Content-Type': mime},
            params={'uploadType': 'media', 'name': name, 'ifGenerationMatch': '0'})
        if response.status_code == 412:
            with self.download(self.bucket, name, session_transport=transport) as existing:
                if existing.content != data:
                    raise APIError(f'Existing Cloud Storage object differs: {name}')
        else:
            response.raise_for_status()
        with self._upload_lock:
            self.uploaded.add(name)

    def upload(self, name, data, mime):
        self._upload_with_transport(None, name, data, mime)

    def download(self, bucket, name, *, session_transport=None):
        url = f'https://storage.googleapis.com/storage/v1/b/{bucket}/o/{quote(name, safe="")}'
        response = self._retryable_request(
            'GET', url, session_transport=session_transport, params={'alt': 'media'}, stream=True)
        response.raise_for_status()
        return response

    def pages(self, url, field, **params):
        while True:
            response = self._retryable_request('GET', url, params=params)
            response.raise_for_status()
            page = response.json()
            yield from page.get(field, [])
            if not page.get('nextPageToken'):
                return
            params['pageToken'] = page['nextPageToken']

    def _upload_images(self, images):
        pending = []
        for name, image in images.items():
            if name in self.uploaded:
                continue
            content = Path(image['path']).read_bytes()
            if digest(content) != image['sha256']:
                raise ValueError(f'Batch image changed: {image["path"]}')
            pending.append((name, content, image['mime']))
        if not pending:
            return
        # If self.upload was patched or overridden in tests, or only a single file is pending, call self.upload directly.
        if type(self).upload is not BatchClient.upload or 'upload' in self.__dict__ or len(pending) == 1:
            for name, content, mime in pending:
                self.upload(name, content, mime)
            return

        def worker(item):
            name, content, mime = item
            transport = getattr(self._thread_local, 'transport', None)
            if transport is None:
                transport = VertexSession(self.api)
                self._thread_local.transport = transport
                self._thread_local.auth_epoch = self._auth_epoch
            self._upload_with_transport(transport, name, content, mime)

        with ThreadPoolExecutor(max_workers=min(UPLOAD_WORKERS, len(pending))) as executor:
            for _ in executor.map(worker, pending):
                pass

    def start(self, folder, manifest):
        state_path = folder / 'job.json'
        if state_path.exists():
            return json.loads(state_path.read_text())
        if self.spent() + manifest['reservation_usd'] > self.config['budget_usd']:
            raise APIError(f'Batch budget guard reached before {folder.name}. '
                           f'This batch requires a reservation of ${manifest["reservation_usd"]:.4f}')
        data = (folder / 'input.jsonl').read_bytes()
        if digest(data) != manifest['input_sha256']:
            raise ValueError(f'Batch input changed: {folder}')
        self._upload_images(manifest['images'])
        root = f'{self.prefix}/{folder.name}'
        self.upload(f'{root}/input.jsonl', data, 'application/jsonl')
        spec = {
            'displayName': f'fashion-{digest(self.uri(root).encode())[:24]}',
            'model': f'publishers/google/models/{self.api["model"]}',
            'inputConfig': {'instancesFormat': 'jsonl',
                            'gcsSource': {'uris': [self.uri(f'{root}/input.jsonl')]}},
            'outputConfig': {'predictionsFormat': 'jsonl',
                             'gcsDestination': {'outputUriPrefix': self.uri(f'{root}/output')}},
        }
        state = {'spec': spec, 'accounted_usd': manifest['reservation_usd']}
        # Persist the reservation and identity before POST. A lost response must never cause a second POST.
        write_json(state_path, state)
        response = self.request('POST', f'{self.transport.base}/batchPredictionJobs', json=spec)
        if not response.ok:
            detail = f'Batch submission HTTP {response.status_code}: {response.text[:500]}'
            if response.status_code in REJECTED_HTTP_STATUSES:
                state_path.unlink()
                raise APIError(f'{detail}. Correct the rejection and run the same command again')
            raise APIError(f'{detail}. Submission state is saved in {state_path}')
        state['name'] = response.json()['name']
        write_json(state_path, state)
        return state

    def wait(self, folder, state):
        if self.transport is None:
            self.transport = VertexSession(self.api)
        base = self.transport.base
        state_path = folder / 'job.json'
        if 'name' not in state:
            spec = state['spec']
            matches = [job for job in self.pages(f'{base}/batchPredictionJobs', 'batchPredictionJobs',
                                                filter=f'displayName="{spec["displayName"]}"')
                       if job.get('displayName') == spec['displayName']
                       and job.get('inputConfig', {}).get('gcsSource') == spec['inputConfig']['gcsSource']
                       and job.get('outputConfig', {}).get('gcsDestination') == spec['outputConfig']['gcsDestination']]
            if len(matches) != 1:
                raise APIError(f'Cannot recover a unique batch job from {state_path}; inspect Vertex before retrying')
            state['name'] = matches[0]['name']
            write_json(state_path, state)
        print(f'{folder.name} {state["name"]}', flush=True)
        last_status = None
        while True:
            response = self._retryable_request('GET', f'{base.split("/v1/", 1)[0]}/v1/{state["name"]}')
            response.raise_for_status()
            job = response.json()
            status = job['state']
            if status in TERMINAL_STATES:
                return job
            if status != last_status:
                print(f'{folder.name} {status}', flush=True)
                last_status = status
            time.sleep(self.config['poll_seconds'])

    def collect(self, folder, manifest, state, job):
        status = job['state']
        if status == 'JOB_STATE_PAUSED':
            raise APIError(f'Batch {state["name"]} is paused')
        entries = manifest['entries']
        directory = job.get('outputInfo', {}).get('gcsOutputDirectory')
        results = {}
        if directory:
            bucket, prefix = directory.removeprefix('gs://').split('/', 1)
            for obj in self.pages(f'https://storage.googleapis.com/storage/v1/b/{bucket}/o', 'items',
                                  prefix=prefix.rstrip('/') + '/'):
                if not obj['name'].endswith('.jsonl'):
                    continue
                with self.download(bucket, obj['name']) as response:
                    for line in response.iter_lines():
                        if not line:
                            continue
                        row = json.loads(line)
                        key = request_key(row['request'])
                        if key not in entries or key in results:
                            raise APIError(f'Unknown or duplicate request in batch output {obj["name"]}')
                        results[key] = row
        missing = [entry['product_id'] for key, entry in entries.items() if key not in results]
        stats = job.get('completionStats') or {}
        processed_count = None
        if {'successfulCount', 'failedCount'} <= stats.keys():
            processed_count = int(stats['successfulCount']) + int(stats['failedCount'])
        # A completed request can be billable even if its output is not visible yet.
        retry_missing = (bool(missing) and status != 'JOB_STATE_SUCCEEDED'
                         and processed_count == len(results))
        if not results and not retry_missing:
            raise APIError(f'Batch {state["name"]} ended as {status} without output: {job.get("error", "")}')
        accounted = 0 if retry_missing else self.per_request * len(missing)
        for key, entry in entries.items():
            if key not in results:
                continue
            row = results[key]
            response = row.get('response') or {}
            usage = response.get('usageMetadata') or {}
            cost = estimated_cost(usage, self.rates) if 'promptTokenCount' in usage else None
            accounted += self.per_request if cost is None else cost
            pid = entry['product_id']
            metadata = {**entry, 'call_id': f'{state["name"]}/{pid}', 'model': self.api['model'],
                        'usage': usage, 'estimated_usd': cost, 'batch_job': state['name']}
            error = row.get('status') or ''
            parsed = None
            if not error:
                try:
                    parsed = parse_response(response)
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    error = f'Invalid batch response: {exc}'
            yield pid, parsed, metadata, str(error)
        write_json(folder / 'job.json', {**state, 'state': status, 'accounted_usd': accounted,
                                         'missing_product_ids': missing, 'retry_missing': retry_missing,
                                         'processed_count': processed_count})
