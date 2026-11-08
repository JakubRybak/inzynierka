"""Offline regression checks for paid-call replay and uncertain outcomes."""
import json
import signal
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from feature_extraction.embeddings.build import build, encode
from feature_extraction.embeddings.client import EmbeddingRejected
from feature_extraction.llm.client import APIError, ExtractionClient
from feature_extraction.settings import load_settings, validate_embedding_settings


SUCCESS = {'usageMetadata': {'promptTokenCount': 100, 'candidatesTokenCount': 10},
           'candidates': [{'finishReason': 'STOP',
                           'content': {'parts': [{'text': '{"value":"ok"}'}]}}]}


class Response:
    def __init__(self, data, status=200, headers=None):
        self.data, self.status_code = data, status
        self.ok, self.text = status == 200, json.dumps(data)
        self.headers = headers or {}

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


def make_embedding_settings(**overrides):
    cfg = {
        'model': 'test',
        'dimension': 2,
        'timeout_seconds': 10,
        'budget_usd': 1.0,
        'max_input_tokens': 100,
        'image_usd_per_million': 0.45,
        'text_usd_per_million': 0.20,
        'concurrency': 1,
        'max_rate_limit_retries': 5,
        'max_auth_retries': 2,
    }
    cfg.update(overrides)
    return {'api': {'project': 'test', 'location': 'global'}, 'embedding_api': cfg}


def make_items(count=2):
    items = []
    for idx in range(1, count + 1):
        pid = str(idx)
        items.append({'product_id': pid, 'modality': 'image', 'content': f'Image-{pid}'.encode(),
                      'input_sha256': f'img-{pid}', 'image_id': f'id-{pid}', 'image_path': f'{pid}.png'})
        items.append({'product_id': pid, 'modality': 'text', 'content': f'Text-{pid}'.encode(),
                      'input_sha256': f'txt-{pid}', 'image_id': f'id-{pid}', 'image_path': f'{pid}.png'})
    return items


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
                                      'text_usd_per_million': .2, 'max_rate_limit_retries': 0}}
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

    def test_embedding_settings_defaults_and_validation(self):
        defaults = validate_embedding_settings({'model': 'm', 'dimension': 2})
        self.assertEqual(defaults['concurrency'], 1)
        self.assertEqual(defaults['max_rate_limit_retries'], 5)
        self.assertEqual(defaults['max_auth_retries'], 2)
        for bad in [{'concurrency': 0}, {'concurrency': -1}, {'concurrency': True},
                    {'max_rate_limit_retries': -1}, {'max_auth_retries': -1}, {'max_auth_retries': False}]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_embedding_settings(bad)
        default_cfg = load_settings()
        self.assertEqual(default_cfg['embedding_api']['concurrency'], 10)
        self.assertEqual(default_cfg['embedding_api']['max_rate_limit_retries'], 5)
        self.assertEqual(default_cfg['embedding_api']['max_auth_retries'], 2)
        pilot_cfg = load_settings(Path('feature_extraction/artifacts/configs/pilot_9922.yaml'))
        self.assertEqual(pilot_cfg['embedding_api']['concurrency'], 10)

    def test_parallel_calls_reuse_per_worker_sessions_and_reduce_4_to_3_to_2_to_1_with_wave_dedup(self):
        settings = make_embedding_settings(concurrency=4, max_rate_limit_retries=5)
        items = make_items(5)  # 10 embedding tasks total
        accepted = Response({'embedding': {'values': [1.0, 0.0]}, 'usageMetadata': {'promptTokenCount': 10}})

        state_lock = threading.Lock()
        active_calls = 0
        max_seen_in_wave = []
        sessions_by_thread = {}
        call_index = 0

        # Wave 1 (calls 1..4): 4 concurrent calls launched. 2 return 429 first, 2 succeed slightly later -> drops 4 -> 3 once.
        # Wave 2 (calls 5..7): 3 concurrent calls launched after Wave 1 finishes. 1 returns 429 first -> drops 3 -> 2.
        # Wave 3 (calls 8..9): 2 concurrent calls launched after Wave 2 finishes. 1 returns 429 first -> drops 2 -> 1.
        # Wave 4+ (call 10+): runs at concurrency 1; call 10 returns 429 at limit 1 -> limit stays at 1.
        barrier_4 = threading.Barrier(4, timeout=5)
        barrier_3 = threading.Barrier(3, timeout=5)
        barrier_2 = threading.Barrier(2, timeout=5)

        class FakeSession:
            def __init__(self, api_cfg):
                tid = threading.get_ident()
                sessions_by_thread.setdefault(tid, []).append(self)

            def refresh(self):
                pass

            def post(self, model, method, body, timeout):
                nonlocal active_calls, call_index
                with state_lock:
                    call_index += 1
                    idx = call_index
                    active_calls += 1
                try:
                    if idx <= 4:
                        barrier_4.wait()
                        if idx in (1, 2):
                            return Response({'error': 'rate limit'}, 429, headers={'Retry-After': '0.02'})
                        time.sleep(0.005)
                        return accepted
                    if idx <= 7:
                        barrier_3.wait()
                        if idx == 5:
                            return Response({'error': 'rate limit'}, 429, headers={'Retry-After': '0.02'})
                        time.sleep(0.005)
                        return accepted
                    if idx <= 9:
                        barrier_2.wait()
                        if idx == 8:
                            return Response({'error': 'rate limit'}, 429, headers={'Retry-After': '0.02'})
                        time.sleep(0.005)
                        return accepted
                    if idx == 10:
                        max_seen_in_wave.append(active_calls)
                        return Response({'error': 'rate limit'}, 429, headers={'Retry-After': '0.01'})
                    max_seen_in_wave.append(active_calls)
                    return accepted
                finally:
                    with state_lock:
                        active_calls -= 1

        logs = []
        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession', FakeSession), \
             patch('feature_extraction.embeddings.build.log_event', side_effect=logs.append):
            folder = Path(directory)
            summary = encode(settings, folder, items, True, None)
            self.assertEqual(summary['cached_vectors'], {'image': 5, 'text': 5})
            self.assertTrue(json.loads((folder / 'manifest.json').read_text())['complete'])
            # Each worker thread created at most 1 FakeSession and reused it
            self.assertTrue(all(len(s) == 1 for s in sessions_by_thread.values()))
            self.assertEqual(len(sessions_by_thread), 4)
            # Check concurrency transitions logged: 4 -> 3, 3 -> 2, 2 -> 1, and stays at 1
            reduction_logs = [m for m in logs if 'reducing concurrency' in m or 'concurrency stays at 1' in m]
            self.assertEqual(sum(1 for m in reduction_logs if '4 -> 3' in m), 1)
            self.assertEqual(sum(1 for m in reduction_logs if '3 -> 2' in m), 1)
            self.assertEqual(sum(1 for m in reduction_logs if '2 -> 1' in m), 1)
            self.assertTrue(any('concurrency stays at 1' in m for m in reduction_logs))
            # After dropping to 1, active concurrency never exceeded 1
            self.assertEqual(max_seen_in_wave, [1] * len(max_seen_in_wave))

    def test_429_exhaustion_at_limit_1_saves_inflight_and_stops_after_six_429_responses(self):
        # 5 retries means 6 total 429 responses for a single embedding task before failing.
        # Concurrency reduction does not reset the per-item retry counter.
        settings = make_embedding_settings(concurrency=2, max_rate_limit_retries=5)
        items = make_items(1)  # 1 image + 1 text
        accepted = Response({'embedding': {'values': [1.0, 0.0]}, 'usageMetadata': {'promptTokenCount': 10}})
        calls = {'image': 0, 'text': 0}
        lock = threading.Lock()

        class FakeSession:
            def __init__(self, api_cfg):
                pass

            def post(self, model, method, body, timeout):
                part = body['content']['parts'][0]
                modality = 'text' if 'text' in part else 'image'
                with lock:
                    calls[modality] += 1
                if modality == 'text':
                    time.sleep(0.02)
                    return accepted
                return Response({'error': '429'}, 429)

        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession', FakeSession), \
             patch('feature_extraction.embeddings.build.RATE_LIMIT_DELAYS', (0.001, 0.001, 0.001, 0.001, 0.001)):
            folder = Path(directory)
            with self.assertRaisesRegex(EmbeddingRejected, 'Rate limit retries exhausted'):
                encode(settings, folder, items, True, None)
            # 1 initial call + 5 retries = 6 calls for image; 1 call for text which succeeded in flight
            self.assertEqual(calls['image'], 6)
            self.assertEqual(calls['text'], 1)
            self.assertTrue((folder / 'cache/text/1.json').exists())
            self.assertFalse((folder / 'cache/image/1.json').exists())
            ledger = json.loads((folder / 'cost_ledger.json').read_text())
            self.assertEqual(sum(1 for r in ledger if r['status'] == 'rejected'), 6)
            self.assertEqual(sum(1 for r in ledger if r['status'] == 'completed'), 1)

    def test_429_shared_pause_never_shortens_existing_pause(self):
        settings = make_embedding_settings(concurrency=2, max_rate_limit_retries=2)
        items = make_items(1)
        accepted = Response({'embedding': {'values': [1.0, 0.0]}, 'usageMetadata': {'promptTokenCount': 10}})
        barrier = threading.Barrier(2, timeout=5)
        call_num = 0
        lock = threading.Lock()

        class FakeSession:
            def __init__(self, api_cfg):
                pass

            def post(self, model, method, body, timeout):
                nonlocal call_num
                with lock:
                    call_num += 1
                    n = call_num
                if n == 1:
                    barrier.wait()
                    return Response({}, 429, headers={'Retry-After': '10'})
                if n == 2:
                    barrier.wait()
                    time.sleep(0.01)
                    return Response({}, 429, headers={'Retry-After': '1'})
                return accepted

        logs = []
        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession', FakeSession), \
             patch('feature_extraction.embeddings.build.pause_for') as mock_pause, \
             patch('feature_extraction.embeddings.build.log_event', side_effect=logs.append):
            clock = [100.0]

            def fake_monotonic():
                return clock[0]

            def fake_pause(seconds):
                clock[0] += seconds

            mock_pause.side_effect = fake_pause
            with patch('feature_extraction.embeddings.build.time.monotonic', side_effect=fake_monotonic):
                encode(settings, Path(directory), items, True, None)
            # First pause after the two 429s must be ~10s, not shortened to 1s
            self.assertGreaterEqual(mock_pause.call_args_list[0].args[0], 9.9)

    def test_401_refreshes_token_twice_without_reducing_concurrency_and_stops_on_third_401(self):
        settings = make_embedding_settings(concurrency=2, max_auth_retries=2)
        items = make_items(1)  # 2 tasks: 1 image, 1 text
        accepted = Response({'embedding': {'values': [1.0, 0.0]}, 'usageMetadata': {'promptTokenCount': 10}})
        refreshes = []
        calls = {'image': 0, 'text': 0}
        lock = threading.Lock()

        class FakeSession:
            def __init__(self, api_cfg):
                pass

            def refresh(self):
                with lock:
                    refreshes.append(threading.get_ident())

            def post(self, model, method, body, timeout):
                part = body['content']['parts'][0]
                modality = 'text' if 'text' in part else 'image'
                with lock:
                    calls[modality] += 1
                    c = calls[modality]
                if modality == 'image':
                    # Fails twice with 401, succeeds on 3rd attempt (2 retries)
                    if c <= 2:
                        return Response({'error': 'unauthenticated'}, 401)
                    return accepted
                # Text fails 3 times with 401 -> exhausts 2 retries
                return Response({'error': 'unauthenticated'}, 401)

        logs = []
        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession', FakeSession), \
             patch('feature_extraction.embeddings.build.log_event', side_effect=logs.append):
            folder = Path(directory)
            with self.assertRaisesRegex(EmbeddingRejected, 'Authentication retries exhausted'):
                encode(settings, folder, items[:1], True, None) if False else encode(settings, folder, items, True, None)
            # Image succeeded on 3rd attempt; text failed on all 3 attempts (initial + 2 retries)
            self.assertEqual(calls['image'], 3)
            self.assertEqual(calls['text'], 3)
            self.assertGreaterEqual(len(refreshes), 2)
            self.assertTrue((folder / 'cache/image/1.json').exists())
            self.assertFalse((folder / 'cache/text/1.json').exists())
            # 401 must never reduce concurrency
            self.assertFalse(any('reducing concurrency' in m for m in logs))

    def test_budget_limit_includes_active_inflight_reservations(self):
        # Each image reserves 100 * 0.45 / 1e6 = 0.000045; each text reserves 100 * 0.20 / 1e6 = 0.000020.
        # Set budget to allow the first 2 reservations (0.000045 + 0.000020 = 0.000065), blocking the 3rd while 1 & 2 are in flight.
        settings = make_embedding_settings(concurrency=4, budget_usd=0.000070)
        items = make_items(2)  # 4 tasks
        accepted = Response({'embedding': {'values': [1.0, 0.0]}, 'usageMetadata': {'promptTokenCount': 10}})
        started = threading.Event()
        release = threading.Event()
        call_count = 0
        lock = threading.Lock()

        class FakeSession:
            def __init__(self, api_cfg):
                pass

            def post(self, model, method, body, timeout):
                nonlocal call_count
                with lock:
                    call_count += 1
                    if call_count == 2:
                        started.set()
                started.wait(timeout=5)
                release.wait(timeout=5)
                return accepted

        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession', FakeSession):
            folder = Path(directory)
            release.set()
            with self.assertRaisesRegex(RuntimeError, 'Persistent embedding budget guard reached'):
                encode(settings, folder, items, True, None)
            # Only 2 calls were started and completed; 3rd was blocked by active reservations
            self.assertEqual(call_count, 2)
            ledger = json.loads((folder / 'cost_ledger.json').read_text())
            self.assertEqual([r['status'] for r in ledger], ['completed', 'completed'])
            # Resuming with higher budget finishes only the remaining 2 tasks
            settings['embedding_api']['budget_usd'] = 1.0
            summary = encode(settings, folder, items, True, None)
            self.assertEqual(summary['missing_vectors_before_run'], 2)
            self.assertEqual(call_count, 4)
            self.assertTrue(json.loads((folder / 'manifest.json').read_text())['complete'])

    def test_sigint_stops_new_submissions_and_saves_inflight_responses(self):
        settings = make_embedding_settings(concurrency=2)
        items = make_items(3)  # 6 tasks
        accepted = Response({'embedding': {'values': [1.0, 0.0]}, 'usageMetadata': {'promptTokenCount': 10}})
        both_started = threading.Barrier(2, timeout=5)
        call_count = 0
        lock = threading.Lock()
        signaled = False

        class FakeSession:
            def __init__(self, api_cfg):
                pass

            def post(self, model, method, body, timeout):
                nonlocal call_count, signaled
                both_started.wait()
                with lock:
                    call_count += 1
                    if not signaled:
                        signaled = True
                        signal.raise_signal(signal.SIGINT)
                time.sleep(0.02)
                return accepted

        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.embeddings.client.VertexSession', FakeSession):
            folder = Path(directory)
            with self.assertRaises(KeyboardInterrupt):
                encode(settings, folder, items, True, None)
            # Only the 2 in-flight calls ran and both were saved to cache and marked completed in ledger
            self.assertEqual(call_count, 2)
            ledger = json.loads((folder / 'cost_ledger.json').read_text())
            self.assertEqual([r['status'] for r in ledger], ['completed', 'completed'])
            cached_files = list((folder / 'cache').rglob('*.json'))
            self.assertEqual(len(cached_files), 2)

            # Resuming from cache computes only the remaining 4 vectors
            class ResumeSession:
                def __init__(self, api_cfg):
                    pass

                def post(self, model, method, body, timeout):
                    nonlocal call_count
                    with lock:
                        call_count += 1
                    return accepted

            with patch('feature_extraction.embeddings.client.VertexSession', ResumeSession):
                summary = encode(settings, folder, items, True, None)
            self.assertEqual(summary['missing_vectors_before_run'], 4)
            self.assertEqual(call_count, 6)
            self.assertTrue(json.loads((folder / 'manifest.json').read_text())['complete'])

    def test_pilot_9922_state_is_ready_to_resume_from_cache(self):
        pilot_path = Path('feature_extraction/artifacts/configs/pilot_9922.yaml')
        if not pilot_path.exists():
            self.skipTest('pilot_9922 config not present')
        settings = load_settings(pilot_path)
        self.assertEqual(settings['embedding_api']['concurrency'], 10)
        summary = build(settings, execute=False)
        # 10,134 products (9,922 selected + 212 external references) -> 20,268 total vectors.
        # 1,800 from pilot_900 + 8,245 from pilot_9922 = 10,045 cached; 10,223 missing (8,245 of 18,468 done).
        self.assertEqual(summary['selected_products_including_references'], 10134)
        self.assertEqual(summary['missing_vectors_before_run'], 10223)
        self.assertEqual(sum(summary['cached_vectors'].values()), 10045)
        run_folder = Path(settings['artifacts']) / 'runs/pilot_9922'
        self.assertFalse((run_folder / 'batch').exists())


if __name__ == '__main__':
    unittest.main()
