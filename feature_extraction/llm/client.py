"""Vertex transport, durable spending reservations and bounded HTTP retries."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from ..storage import digest, write_json
from .request import estimated_cost, parse_response, request_body


REJECTED_HTTP_STATUSES = {400, 401, 403, 404, 429}


class APIError(RuntimeError):
    """An API response that should stop the extraction job."""


class VertexSession:
    def __init__(self, config):
        import google.auth
        from google.auth.transport.requests import AuthorizedSession, Request
        credentials, _ = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform'],
            quota_project_id=config['project'])
        credentials.refresh(Request())
        self.session = AuthorizedSession(credentials.with_quota_project(config['project']),
                                         max_refresh_attempts=0)
        location = config['location']
        host = 'aiplatform.googleapis.com' if location == 'global' else f'{location}-aiplatform.googleapis.com'
        self.base = f'https://{host}/v1/projects/{config["project"]}/locations/{location}'

    def post(self, model, method, body, timeout):
        return self.session.post(f'{self.base}/publishers/google/models/{model}:{method}', json=body, timeout=timeout)




class ExtractionClient:
    def __init__(self, config, requests_folder):
        self.config = config
        self.folder = Path(requests_folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.transport = None

    def spent(self):
        return sum(json.loads(p.read_text())['accounted_usd'] for p in self.folder.glob('*_attempt_*.json'))

    def finish_response(self, path, attempt):
        try:
            data = attempt['response']
            usage = data['usageMetadata']
            cost = estimated_cost(usage, self.config)
            attempt.update(usage=usage, estimated_usd=cost, accounted_usd=cost)
            parsed = parse_response(data)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            attempt.update(status='invalid_response', error=str(error))
            write_json(path, attempt)
            raise APIError(f'Invalid saved response for {attempt["product_id"]}: {error}') from error
        attempt.update(status='completed', parsed_output=parsed)
        write_json(path, attempt)
        return parsed, attempt

    def generate(self, product_id, prompt, context):
        cfg = self.config
        body, images = request_body(prompt, cfg['max_output_tokens'])
        request_hash = digest(json.dumps(body, sort_keys=True).encode())
        prior = sorted(self.folder.glob(f'{product_id}_attempt_*.json'),
                       key=lambda path: int(path.stem.rsplit('_', 1)[-1]))
        unresolved = False
        for path in prior:
            attempt = json.loads(path.read_text())
            if attempt['request_sha256'] != request_hash:
                raise APIError(f'Changed request for {product_id}; use a new run name')
            if attempt['status'] == 'completed':
                return attempt['parsed_output'], attempt
            if attempt.get('http_status') in REJECTED_HTTP_STATUSES:
                if attempt['status'] != 'rejected':
                    attempt.update(status='rejected', accounted_usd=0)
                    write_json(path, attempt)
                continue
            if attempt['status'] == 'reserved' and attempt.get('http_status') == 200:
                return self.finish_response(path, attempt)
            unresolved = True
        if unresolved:
            raise APIError(f'Unresolved previous attempt for {product_id}; inspect before paying again')
        if self.transport is None:
            self.transport = VertexSession(cfg)
        counted = self.transport.post(cfg['model'], 'countTokens', body, 60)
        if not counted.ok:
            raise APIError(f'countTokens HTTP {counted.status_code}: {counted.text[:500]}')
        tokens = counted.json()['totalTokens']
        if tokens > cfg['max_input_tokens']:
            raise APIError('Input token guard reached')
        input_rate = cfg['input_usd_per_million'] / 1_000_000
        output_rate = cfg['output_usd_per_million'] / 1_000_000
        allowance = len(json.dumps(body['generationConfig']['responseSchema']).encode()) + 2048
        reservation = (tokens + allowance) * input_rate + cfg['max_output_tokens'] * output_rate
        last_attempt = int(prior[-1].stem.rsplit('_', 1)[-1]) if prior else 0
        for number in range(last_attempt + 1, last_attempt + cfg['max_attempts'] + 1):
            if self.spent() + reservation > cfg['budget_usd']:
                raise APIError('Persistent budget guard reached before inference')
            path = self.folder / f'{product_id}_attempt_{number}.json'
            attempt = {'call_id': f'{self.folder.parent.name}/{product_id}/{number}',
                       'product_id': product_id, 'attempt': number, 'status': 'reserved',
                       'started_at_utc': datetime.now(timezone.utc).isoformat(),
                       'request_sha256': request_hash, 'images': images, **context,
                       'model': cfg['model'], 'generation_config': body['generationConfig'],
                       'accounted_usd': reservation, 'reservation_usd': reservation}
            write_json(path, attempt)
            start = time.monotonic()
            try:
                response = self.transport.post(cfg['model'], 'generateContent', body, cfg['timeout_seconds'])
            except Exception as error:
                attempt.update(status='transport_uncertain', error=str(error), seconds=time.monotonic()-start)
                write_json(path, attempt)
                raise APIError('Transport outcome uncertain; inspect saved reservation before retrying') from error
            attempt.update(seconds=time.monotonic()-start, http_status=response.status_code)
            try:
                attempt['response'] = response.json()
            except ValueError:
                attempt['response_text'] = response.text[:2000]
            write_json(path, attempt)
            if not response.ok:
                rejected = response.status_code in REJECTED_HTTP_STATUSES
                attempt.update(status='rejected' if rejected else 'http_error',
                               error=f'HTTP {response.status_code}',
                               accounted_usd=0 if rejected else reservation)
                write_json(path, attempt)
                if response.status_code == 429 and number < last_attempt + cfg['max_attempts']:
                    time.sleep(cfg['retry_delay_seconds'])
                    continue
                raise APIError(f'generateContent HTTP {response.status_code}; inspect {path}')
            return self.finish_response(path, attempt)
