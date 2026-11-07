"""Exercise the batch lifecycle without contacting Google Cloud."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from feature_extraction.llm.batch import BatchClient
from feature_extraction.llm.client import APIError
from feature_extraction.pipeline import extract_batches
from feature_extraction.storage import read_jsonl


API = {'model': 'test', 'max_input_tokens': 1000, 'max_output_tokens': 100}
CONFIG = {'bucket': 'test-bucket', 'prefix': 'fashiongen', 'poll_seconds': 1,
          'budget_usd': 1, 'input_usd_per_million': .15, 'output_usd_per_million': 1.25}
JOB_NAME = 'projects/test/locations/global/batchPredictionJobs/123'
JOB = {'name': JOB_NAME, 'state': 'JOB_STATE_SUCCEEDED',
       'outputInfo': {'gcsOutputDirectory': 'gs://test-bucket/batch-output'}}


def record(pid):
    return dict(product_id=pid, brand='Brand', category='T-shirts', section='Tops',
                features={}, feature_metadata={}, status='pending', exclusion_reasons=[])


def prompt(pid):
    return {'system_instruction': 'Classify', 'parts': [{'text': pid}],
            'generation_config': {'responseSchema': {'type': 'OBJECT'}}}


def response(data):
    return Mock(ok=True, json=Mock(return_value=data))


class BatchTests(unittest.TestCase):
    def test_budget_blocks_upload_and_submission(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / '000001'
            client = BatchClient(API, {**CONFIG, 'budget_usd': .00001}, folder.parent, 'fp')
            manifest = client.prepare(folder, [('1', prompt('1'), {})])
            client.request = Mock()
            with self.assertRaisesRegex(APIError, 'budget guard'):
                client.start(folder, manifest)
            client.request.assert_not_called()

    def test_definitive_submission_rejection_releases_reservation(self):
        for status in (400, 403, 429):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory) / '000001'
                client = BatchClient(API, CONFIG, folder.parent, 'fp')
                client.transport = Mock(base='https://aiplatform.googleapis.com/v1/projects/test/locations/global')
                client.upload = Mock()
                client.request = Mock(side_effect=[Mock(ok=False, status_code=status, text='Rejected'),
                                                   response(JOB)])
                manifest = client.prepare(folder, [('1', prompt('1'), {})])
                with self.assertRaisesRegex(APIError, 'run the same command again'):
                    client.start(folder, manifest)
                self.assertEqual(client.spent(), 0)
                self.assertEqual(client.start(folder, manifest)['name'], JOB_NAME)
                self.assertEqual([call.args[0] for call in client.request.call_args_list], ['POST', 'POST'])

    def test_recovers_lost_submission_without_sending_again(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / '000001'
            client = BatchClient(API, CONFIG, folder.parent, 'fp')
            client.transport = Mock(base='https://aiplatform.googleapis.com/v1/projects/test/locations/global')
            client.upload = Mock()
            client.request = Mock(side_effect=TimeoutError())
            manifest = client.prepare(folder, [('1', prompt('1'), {})])
            with self.assertRaises(TimeoutError):
                client.start(folder, manifest)
            state = client.start(folder, manifest)
            client.request.assert_called_once()
            client.pages = Mock(return_value=[{**state['spec'], 'name': JOB_NAME}])
            client.request = Mock(return_value=response(JOB))
            self.assertEqual(client.wait(folder, state), JOB)
            self.assertEqual(client.request.call_args.args[0], 'GET')
            self.assertEqual(json.loads((folder / 'job.json').read_text())['name'], JOB_NAME)

    def test_collection_matches_out_of_order_rows_and_records_row_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / '000001'
            client = BatchClient(API, CONFIG, folder.parent, 'fp')
            manifest = client.prepare(folder, [('1', prompt('1'), {}), ('2', prompt('2'), {})])
            first, second = read_jsonl(folder / 'input.jsonl')
            second['request']['contents'][0]['parts'][0]['fileData'] = None
            first['status'] = 'Invalid input'
            second['response'] = {
                'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': '{"ok": true}'}]}}],
                'usageMetadata': {'promptTokenCount': 50, 'candidatesTokenCount': 5, 'thoughtsTokenCount': 3},
            }
            cloud_file = Mock(iter_lines=Mock(return_value=[json.dumps(row) for row in (second, first)]))
            client.pages = Mock(return_value=[{'name': 'batch-output/predictions.jsonl'}])
            client.download = patch_download = Mock()
            patch_download.return_value.__enter__ = Mock(return_value=cloud_file)
            patch_download.return_value.__exit__ = Mock(return_value=False)
            rows = list(client.collect(folder, manifest, {'name': JOB_NAME}, JOB))
            self.assertEqual([(pid, parsed, error) for pid, parsed, _, error in rows],
                             [('1', None, 'Invalid input'), ('2', {'ok': True}, '')])
            self.assertAlmostEqual(client.spent(), client.per_request + .0000175)

    def test_missing_output_from_successful_job_remains_reserved(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / '000001'
            client = BatchClient(API, CONFIG, folder.parent, 'fp')
            manifest = client.prepare(folder, [('1', prompt('1'), {}), ('2', prompt('2'), {})])
            first = read_jsonl(folder / 'input.jsonl')[0]
            first['status'] = 'Invalid input'
            stream = Mock(iter_lines=Mock(return_value=[json.dumps(first)]))
            stream.__enter__ = Mock(return_value=stream)
            stream.__exit__ = Mock(return_value=False)
            client.pages = Mock(return_value=[{'name': 'predictions.jsonl'}])
            client.download = Mock(return_value=stream)
            rows = list(client.collect(folder, manifest, {'name': JOB_NAME}, JOB))
            state = json.loads((folder / 'job.json').read_text())
            self.assertEqual([row[0] for row in rows], ['1'])
            self.assertEqual(state['missing_product_ids'], ['2'])
            self.assertFalse(state['retry_missing'])
            self.assertAlmostEqual(client.spent(), manifest['reservation_usd'])
            cancelled = {**JOB, 'state': 'JOB_STATE_CANCELLED'}
            list(client.collect(folder, manifest, {'name': JOB_NAME}, cancelled))
            state = json.loads((folder / 'job.json').read_text())
            self.assertIsNone(state['processed_count'])
            self.assertFalse(state['retry_missing'])
            self.assertAlmostEqual(client.spent(), manifest['reservation_usd'])

    def test_cancelled_job_with_confirmed_zero_processed_can_retry_all(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / '000001'
            client = BatchClient(API, CONFIG, folder.parent, 'fp')
            manifest = client.prepare(folder, [('1', prompt('1'), {}), ('2', prompt('2'), {})])
            cancelled = {'state': 'JOB_STATE_CANCELLED',
                         'completionStats': {'successfulCount': '0', 'failedCount': '0'}}
            self.assertEqual(list(client.collect(folder, manifest, {'name': JOB_NAME}, cancelled)), [])
            state = json.loads((folder / 'job.json').read_text())
            self.assertEqual(state['processed_count'], 0)
            self.assertTrue(state['retry_missing'])
            self.assertEqual(state['missing_product_ids'], ['1', '2'])
            self.assertEqual(client.spent(), 0)

    def test_parts_use_prior_results_and_finished_parts_are_not_resubmitted(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            records = {}
            keywords = {pid: record(pid) for pid in ('a', 'b', 'c')}
            bank = Mock(bank={})
            bank.add.side_effect = lambda item: bank.bank.update({item['product_id']: item})

            def prepare(item, *args):
                return prompt(item['product_id']), {'bank_size_before': len(bank.bank)}

            def collect(batch_folder, manifest, state, job):
                for entry in manifest['entries'].values():
                    yield entry['product_id'], {}, entry, ''

            arguments = ({'api': API, 'batch': CONFIG}, folder, list(keywords), {}, {}, keywords,
                         records, bank, {}, 'fp', True, 2)
            with patch('feature_extraction.pipeline.prepare_request', side_effect=prepare), \
                 patch('feature_extraction.pipeline.apply_response',
                       side_effect=lambda original, parsed, metadata, error: {
                           **original, 'status': 'ready', 'llm_metadata': metadata}), \
                 patch.object(BatchClient, 'start', return_value={'name': JOB_NAME}) as start, \
                 patch.object(BatchClient, 'wait', return_value=JOB), \
                 patch.object(BatchClient, 'collect', side_effect=collect):
                summary = extract_batches(*arguments)
                self.assertTrue(summary['complete'])
                self.assertEqual(summary['batches_completed'], 2)
                self.assertEqual(start.call_count, 2)
                self.assertEqual([r['llm_metadata']['bank_size_before']
                                  for r in read_jsonl(folder / 'products.jsonl')], [0, 0, 2])
                extract_batches(*arguments)
                self.assertEqual(start.call_count, 2)


    def test_cancelled_part_saves_returned_rows_and_retries_only_missing_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            keywords = {pid: record(pid) for pid in ('a', 'b', 'c')}
            submissions = []

            def start(client, batch_folder, manifest):
                state_path = batch_folder / 'job.json'
                if state_path.exists():
                    self.fail(f'Submitted an existing job again: {batch_folder.name}')
                submissions.append([entry['product_id'] for entry in manifest['entries'].values()])
                return {'name': f'{JOB_NAME}-{batch_folder.name}'}

            def wait(client, batch_folder, state):
                status = 'JOB_STATE_CANCELLED' if batch_folder.name == '000001' else JOB['state']
                job = {**JOB, 'state': status, 'name': state['name']}
                if status == 'JOB_STATE_CANCELLED':
                    job['completionStats'] = {'successfulCount': '1', 'failedCount': '0'}
                return job

            def download(client, bucket, name):
                batch_folder = client.folder / f'{len(submissions):06d}'
                rows = read_jsonl(batch_folder / 'input.jsonl')
                if len(submissions) == 1:
                    rows = rows[:1]
                for row in rows:
                    row['response'] = {
                        'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': '{}'}]}}],
                        'usageMetadata': {'promptTokenCount': 50, 'candidatesTokenCount': 5},
                    }
                stream = Mock(iter_lines=Mock(return_value=[json.dumps(row) for row in rows]))
                stream.__enter__ = Mock(return_value=stream)
                stream.__exit__ = Mock(return_value=False)
                return stream

            def run_part(records):
                bank = Mock(bank={})
                bank.add.side_effect = lambda item: bank.bank.update({item['product_id']: item})
                return extract_batches({'api': API, 'batch': CONFIG}, folder, list(keywords), {}, {},
                                       keywords, records, bank, {}, 'fp', True, 2)

            with patch('feature_extraction.pipeline.prepare_request',
                       side_effect=lambda item, *_: (prompt(item['product_id']), {})), \
                 patch('feature_extraction.pipeline.apply_response',
                       side_effect=lambda original, parsed, metadata, error: {
                           **original, 'status': 'ready', 'llm_metadata': metadata}), \
                 patch.object(BatchClient, 'start', autospec=True, side_effect=start), \
                 patch.object(BatchClient, 'wait', autospec=True, side_effect=wait), \
                 patch.object(BatchClient, 'download', autospec=True, side_effect=download), \
                 patch.object(BatchClient, 'pages', return_value=[{'name': 'predictions.jsonl'}]):
                with self.assertRaisesRegex(APIError, 'no result for 1 products'):
                    run_part({})
                partial = json.loads((folder / 'summary.json').read_text())
                self.assertFalse(partial['complete'])
                self.assertEqual(partial['planned_calls'], 1)
                saved = {item['product_id']: item for item in read_jsonl(folder / 'products.jsonl')}
                self.assertEqual(set(saved), {'a'})
                self.assertTrue(run_part(saved)['complete'])
                self.assertEqual(submissions, [['a', 'b'], ['b'], ['c']])
