"""A saved keyword-only dataset must still enter missing-feature preparation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from feature_extraction.keywords.engine import load_config
from feature_extraction.schema import allowed_values, load_schemas
from feature_extraction.llm.prompt_builder import SCHEMAS
from feature_extraction.pipeline import run
from feature_extraction.settings import BASE


class Bank:
    def __init__(self, *args):
        self.bank = {}

    def examples(self, record):
        references = []
        labels = {key: record['features'].get(key, sorted(allowed_values(rule))[0])
                  for key, rule in SCHEMAS[(record['section'], record['category'])].items()}
        for index in range(2):
            references.append({'record': {**record, 'product_id': str(index), 'status': 'ready', 'features': labels},
                               'source': {'name': 'Reference', 'description': ''}, 'images': []})
        return references, []


class PipelineTests(unittest.TestCase):
    def test_embedding_preview_stops_before_inference_when_vectors_are_missing(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.pipeline.load_inputs', return_value=()) as load, \
             patch('feature_extraction.pipeline.build_embedding_export',
                   return_value={'missing_vectors_before_run': 2}) as build, \
             patch('feature_extraction.pipeline.extract') as extract:
            settings = {'artifacts': directory}
            summary = run(settings, 'preview', limit=3, build_embeddings=True)
            self.assertEqual(summary['stage'], 'embeddings')
            self.assertFalse(summary['complete'])
            self.assertEqual(summary['embeddings']['missing_vectors_before_run'], 2)
            load.assert_called_once_with(settings, 3)
            build.assert_called_once_with(settings, execute=False, catalog=(),
                                          export_folder=Path(directory) / 'runs/preview/embeddings')
            extract.assert_not_called()

    def test_combined_run_reuses_its_export_after_inference_has_started(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch('feature_extraction.pipeline.load_inputs', return_value=()) as load, \
             patch('feature_extraction.pipeline.build_embedding_export',
                   return_value={'missing_vectors_before_run': 2}) as build, \
             patch('feature_extraction.pipeline.extract') as extract:
            settings = {'artifacts': directory, 'embeddings': 'shared'}
            folder = Path(directory) / 'runs/combined'

            def start_inference(run_settings, run_folder, stage, execute, mode, batch_size, catalog):
                self.assertEqual(run_settings['embeddings'], str(folder / 'embeddings'))
                self.assertEqual(run_folder, folder)
                self.assertTrue(execute)
                (folder / 'config.json').write_text('{}')
                return {'complete': False}

            extract.side_effect = start_inference
            run(settings, 'combined', execute=True, limit=3, build_embeddings=True)
            summary = run(settings, 'combined', execute=True, limit=3, build_embeddings=True)
            build.assert_called_once_with(settings, execute=True, catalog=(),
                                          export_folder=folder / 'embeddings')
            self.assertEqual(load.call_count, 2)
            self.assertEqual(extract.call_count, 2)
            self.assertEqual(summary['embeddings'], {'reused_run_export': True})
            self.assertEqual(settings['embeddings'], 'shared')

    def test_pending_keyword_records_are_not_treated_as_completed_llm_records(self):
        schemas, _ = load_schemas()
        configs, _ = load_config(BASE / 'keywords/definitions', schemas)
        product = dict(product_id='target', name='Black tee', description='', brand='Brand',
                       section='Tops', category='T-shirts', gender='Men', composition='100% cotton')
        inputs = (['target'], {'target': product}, {'target': []}, [], configs, schemas)
        with tempfile.TemporaryDirectory() as directory:
            settings = {'artifacts': directory, 'embeddings': str(Path(directory) / 'embeddings'),
                        'api': {'thinking_level': 'MEDIUM', 'media_resolution': 'MEDIA_RESOLUTION_MEDIUM',
                                'budget_usd': 1}}
            with patch('feature_extraction.pipeline.load_inputs', return_value=inputs), \
                 patch('feature_extraction.pipeline.ReferenceBank', Bank):
                run(settings, 'test', stage='keywords')
                summary = run(settings, 'test', stage='llm')
                self.assertEqual(summary['planned_calls_this_invocation'], 1)
                self.assertFalse(summary['complete'])
                self.assertEqual(summary['accounted_usd'], 0)
                settings['api']['budget_usd'] = 5
                resumed = run(settings, 'test', stage='llm')
                self.assertEqual(resumed['planned_calls_this_invocation'], 1)
                products = Path(directory) / 'runs/test/products.jsonl'
                previous = products.read_bytes()
                with self.assertRaisesRegex(ValueError, 'separate keyword run name'):
                    run(settings, 'test', stage='keywords')
                self.assertEqual(products.read_bytes(), previous)


if __name__ == '__main__':
    unittest.main()
