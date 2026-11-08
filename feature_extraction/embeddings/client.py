"""Single-modality embedding requests through the shared Vertex transport."""
import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ..llm.client import APIError, REJECTED_HTTP_STATUSES, VertexSession


def parse_retry_after(headers):
    if not headers:
        return None
    raw = None
    if hasattr(headers, 'get'):
        raw = headers.get('Retry-After') or headers.get('retry-after')
    if raw is None:
        return None
    raw = str(raw).strip()
    if not raw:
        return None
    try:
        delay = float(raw)
        if delay >= 0:
            return delay
    except ValueError:
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delay = (dt - datetime.now(timezone.utc)).total_seconds()
            return max(0.0, delay)
        except Exception:
            return None
    return None


class EmbeddingRejected(APIError):
    """Vertex explicitly rejected the embedding request."""

    def __init__(self, message, status_code=None, retry_after=None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class EmbeddingClient:
    def __init__(self, api_config, embedding_config):
        self.transport = VertexSession(api_config)
        self.config = embedding_config

    def refresh(self):
        if hasattr(self.transport, 'refresh'):
            self.transport.refresh()

    def encode(self, content, modality):
        part = {'text': content.decode('utf-8')} if modality == 'text' else {
            'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(content).decode()}}
        response = self.transport.post(self.config['model'], 'embedContent',
                                       {'content': {'parts': [part]},
                                        'outputDimensionality': self.config['dimension']},
                                       self.config['timeout_seconds'])
        if not response.ok:
            error = f'Embedding HTTP {response.status_code}: {response.text[:500]}'
            if response.status_code in REJECTED_HTTP_STATUSES:
                retry_after = parse_retry_after(getattr(response, 'headers', None))
                raise EmbeddingRejected(error, status_code=response.status_code, retry_after=retry_after)
            raise APIError(error)
        return response.json()
