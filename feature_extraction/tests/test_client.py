"""Offline regression checks for paid-call replay and uncertain outcomes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from feature_extraction.embeddings.build import encode
from feature_extraction.embeddings.client import EmbeddingRejected
from feature_extraction.llm.client import APIError, ExtractionClient


SUCCESS = {'usageMetadata': {'promptTokenCount': 100, 'candidatesTokenCount': 10},
           'candidates': [{'finishReason': 'STOP',
                           'content': {'parts': [{'text': '{"value":"ok"}'}]}}]}


class Response:
    def __init__(self, data, status=200):
        self.data, self.status_code = data, status
        self.ok, self.text = status == 200, json.dumps(data)

    def json(self):
        return self.data


class Transport:
    def __init__(self, outcome):
        self.outcome, self.methods = outcome, []

    def post(self, model, method, body, timeout):
        self.methods.append(method)
        if method == 'countTokens':
            return Response({'totalTokens': 100})
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class ClientTests(unittest.TestCase):
    def config(self):
        return dict(model='test', max_output_tokens=100, max_input_tokens=1000, budget_usd=1,
                    input_usd_per_million=.3, output_usd_per_million=2.5,
                    max_attempts=2, timeout_seconds=10, retry_delay_seconds=0)

    def prompt(self):
        return dict(system_instruction='Classify', parts=[{'text': 'Product'}],
                    generation_config={'responseSchema': {'type': 'OBJECT'}})

    def test_completed_request_replays_without_another_call(self):
        with tempfile.TemporaryDirectory() as folder:
            client = ExtractionClient(self.config(), folder)
            client.transport = Transport(Response(SUCCESS))
            first, _ = client.generate('1', self.prompt(), {})
            second, _ = client.generate('1', self.prompt(), {})
            self.assertEqual(first, second)
            self.assertEqual(client.transport.methods, ['countTokens', 'generateContent'])
            self.assertAlmostEqual(client.spent(), .000055)

    def test_saved_http_success_is_replayed_after_interruption(self):
        with tempfile.TemporaryDirectory() as folder:
            client = ExtractionClient(self.config(), folder)
            client.transport = Transport(Response(SUCCESS))
            with patch.object(client, 'finish_response', side_effect=KeyboardInterrupt), \
                 self.assertRaises(KeyboardInterrupt):
                client.generate('1', self.prompt(), {})
            resumed = ExtractionClient(self.config(), folder)
            resumed.transport = Mock()
            parsed, attempt = resumed.generate('1', self.prompt(), {})
            self.assertEqual(parsed, {'value': 'ok'})
            self.assertEqual(attempt['status'], 'completed')
            self.assertAlmostEqual(resumed.spent(), .000055)
            resumed.transport.post.assert_not_called()

    def test_online_rejections_allow_resume_and_release_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            client = ExtractionClient(self.config(), folder)
            client.transport = Transport(Response({}, 429))
            with self.assertRaisesRegex(APIError, 'HTTP 429'):
                client.generate('1', self.prompt(), {})
            self.assertEqual(client.spent(), 0)
            self.assertEqual(client.transport.methods, ['countTokens', 'generateContent', 'generateContent'])
            resumed = ExtractionClient(self.config(), folder)
            resumed.transport = Transport(Response(SUCCESS))
            _, attempt = resumed.generate('1', self.prompt(), {})
            self.assertEqual(attempt['attempt'], 3)
            self.assertAlmostEqual(resumed.spent(), .000055)

    def test_embedding_rejection_allows_resume_and_releases_budget(self):
        settings = {'api': {'project': 'test', 'location': 'global'},
                    'embedding_api': {'model': 'test', 'dimension': 2, 'timeout_seconds': 10,
                                      'budget_usd': 1, 'max_input_tokens': 100,
                                      'text_usd_per_million': .2}}
        items = [{'product_id': '1', 'modality': 'text', 'content': b'Product', 'input_sha256': 'text'},
                 {'product_id': '1', 'modality': 'image', 'content': b'Image', 'input_sha256': 'image',
                  'image_id': 'image', 'image_path': 'image.png'}]
        settings['embedding_api']['image_usd_per_million'] = .45
        accepted = Response({'embedding': {'values': [1, 0]}, 'usageMetadata': {'promptTokenCount': 10}})
        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession') as transport:
            folder = Path(directory)
            transport.return_value.post.side_effect = [Response({}, 429), accepted, accepted]
            with self.assertRaisesRegex(EmbeddingRejected, 'HTTP 429'):
                encode(settings, folder, items, True, None)
            ledger = folder / 'cost_ledger.json'
            self.assertEqual(json.loads(ledger.read_text())[0]['accounted_usd'], 0)
            encode(settings, folder, items, True, None)
            self.assertEqual([row['status'] for row in json.loads(ledger.read_text())],
                             ['rejected', 'completed', 'completed'])
            self.assertTrue(json.loads((folder / 'manifest.json').read_text())['complete'])
            self.assertEqual(transport.return_value.post.call_count, 3)

    def test_uncertain_transport_retains_reservation_and_blocks_repayment(self):
        with tempfile.TemporaryDirectory() as folder:
            client = ExtractionClient(self.config(), folder)
            client.transport = Transport(TimeoutError('timeout'))
            with self.assertRaises(APIError):
                client.generate('1', self.prompt(), {})
            with self.assertRaises(APIError):
                client.generate('1', self.prompt(), {})
            self.assertEqual(client.transport.methods, ['countTokens', 'generateContent'])
            self.assertGreater(client.spent(), 0)

    def test_budget_stops_before_inference(self):
        with tempfile.TemporaryDirectory() as folder:
            config = self.config()
            config['budget_usd'] = .000001
            client = ExtractionClient(config, folder)
            client.transport = Transport(None)
            with self.assertRaises(APIError):
                client.generate('1', self.prompt(), {})
            self.assertEqual(client.transport.methods, ['countTokens'])
            self.assertEqual(list(Path(folder).glob('*_attempt_*.json')), [])


if __name__ == '__main__':
    unittest.main()
