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
    def test_pending_keyword_records_are_not_treated_as_completed_llm_records(self):
        schemas, _ = load_schemas()
        configs, _ = load_config(BASE / 'keywords/definitions', schemas)
        product = dict(product_id='target', name='Black tee', description='', brand='Brand',
                       section='Tops', category='T-shirts', gender='Men', composition='100% cotton')
        inputs = (['target'], {'target': product}, {'target': []}, [], configs, schemas)
        with tempfile.TemporaryDirectory() as directory:
            settings = {'artifacts': directory, 'embeddings': str(Path(directory) / 'embeddings'),
                        'api': {'thinking_level': 'MEDIUM', 'media_resolution': 'MEDIA_RESOLUTION_MEDIUM'}}
            with patch('feature_extraction.pipeline.load_inputs', return_value=inputs), \
                 patch('feature_extraction.pipeline.ReferenceBank', Bank):
                run(settings, 'test', stage='keywords')
                summary = run(settings, 'test', stage='llm')
                self.assertEqual(summary['planned_calls_this_invocation'], 1)
                self.assertFalse(summary['complete'])
                self.assertEqual(summary['accounted_usd'], 0)


if __name__ == '__main__':
    unittest.main()
