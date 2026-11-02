"""Offline regression checks for paid-call replay and uncertain outcomes."""
import json
import tempfile
import unittest
from pathlib import Path

from feature_extraction.llm.client import APIError, ExtractionClient


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
        response = Response({'usageMetadata': {'promptTokenCount': 100, 'candidatesTokenCount': 10},
                             'candidates': [{'finishReason': 'STOP',
                                             'content': {'parts': [{'text': '{"value":"ok"}'}]}}]})
        with tempfile.TemporaryDirectory() as folder:
            client = ExtractionClient(self.config(), folder)
            client.transport = Transport(response)
            first, _ = client.generate('1', self.prompt(), {})
            second, _ = client.generate('1', self.prompt(), {})
            self.assertEqual(first, second)
            self.assertEqual(client.transport.methods, ['countTokens', 'generateContent'])
            self.assertAlmostEqual(client.spent(), .000055)

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
