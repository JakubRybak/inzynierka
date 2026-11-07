"""Build Vertex requests and decode completed model responses."""
import base64
import json
from pathlib import Path

from ..storage import digest


def request_body(prompt, max_output_tokens, image_uri=None):
    parts, images = [], []
    for part in prompt['parts']:
        if 'text' in part:
            parts.append(part)
            continue
        path = Path(part['local_image_path'])
        content = path.read_bytes()
        mime = 'image/jpeg' if path.suffix.lower() in {'.jpg', '.jpeg'} else 'image/png'
        sha = digest(content)
        images.append({'path': str(path), 'sha256': sha})
        if image_uri is None:
            parts.append({'inlineData': {'mimeType': mime, 'data': base64.b64encode(content).decode()}})
        else:
            parts.append({'fileData': {'mimeType': mime, 'fileUri': image_uri(sha, mime, path)}})
    return {'systemInstruction': {'parts': [{'text': prompt['system_instruction']}]},
            'contents': [{'role': 'user', 'parts': parts}],
            'generationConfig': {**prompt['generation_config'], 'maxOutputTokens': max_output_tokens}}, images


def parse_response(data):
    candidate = data['candidates'][0]
    if candidate.get('finishReason') != 'STOP':
        raise ValueError(f'Incomplete output: {candidate.get("finishReason")}')
    text = ''.join(p.get('text', '') for p in candidate['content']['parts'] if not p.get('thought'))
    return json.loads(text)


def estimated_cost(usage, config):
    return (usage['promptTokenCount'] * config['input_usd_per_million']
            + (usage.get('candidatesTokenCount', 0) + usage.get('thoughtsTokenCount', 0))
            * config['output_usd_per_million']) / 1_000_000
