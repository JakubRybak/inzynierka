"""Single-modality embedding requests through the shared Vertex transport."""
import base64

from ..llm.client import VertexSession


class EmbeddingClient:
    def __init__(self, api_config, embedding_config):
        self.transport = VertexSession(api_config)
        self.config = embedding_config

    def encode(self, content, modality):
        part = {'text': content.decode('utf-8')} if modality == 'text' else {
            'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(content).decode()}}
        response = self.transport.post(self.config['model'], 'embedContent',
                                       {'content': {'parts': [part]},
                                        'outputDimensionality': self.config['dimension']},
                                       self.config['timeout_seconds'])
        if not response.ok:
            raise RuntimeError(f'Embedding HTTP {response.status_code}: {response.text[:500]}')
        return response.json()
