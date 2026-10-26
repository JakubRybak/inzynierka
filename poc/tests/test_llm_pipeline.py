"""Offline checks for immutable keyword values and structured-output decisions."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'poc/scripts'))
from build_prompt import requested_rules, validate_response
from llm_pipeline import Dataset, example_images


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = Dataset()
        cls.results = {r['product_id']: r for r in map(json.loads, (ROOT / 'poc/feature_extraction/runs/smoke_6/products.jsonl').read_text().splitlines())}
        cls.calls = {pid: json.loads((ROOT / 'poc/feature_extraction/runs/smoke_6/calls' / (pid + '.json')).read_text()) for pid in cls.results}

    def test_actual_requests_use_exact_views_and_distinct_eligible_neighbors(self):
        d = self.dataset
        for pid, call in self.calls.items():
            self.assertEqual([n['modality'] for n in call['neighbors']], ['image', 'text'])
            self.assertEqual(len({n['product_id'] for n in call['neighbors']}), 2)
            for neighbor in call['neighbors']:
                ref = d.bank[neighbor['product_id']]
                self.assertNotEqual(pid, ref['product_id'])
                self.assertEqual(ref['category'], d.keywords[pid]['category'])
                self.assertEqual(ref['features']['gender'], d.keywords[pid]['features']['gender'])
                self.assertEqual(neighbor['image_ids'], [f"{ref['product_id']}_id_gridfs_1", f"{ref['product_id']}_id_gridfs_3"])
            self.assertEqual(len(call['images']), len(d.images[pid]) + 4)

    def test_actual_outputs_preserve_keywords_and_only_complete_missing_fields(self):
        for pid, call in self.calls.items():
            before = self.dataset.keywords[pid]
            output = call['parsed_output']
            self.assertEqual(set(output['features']), set(requested_rules(before)))
            merged = validate_response(output, before)
            self.assertEqual(merged, self.results[pid]['features'])
            for key, value in before['features'].items():
                self.assertEqual(merged[key], value)

    def test_extra_or_keyword_fields_are_rejected(self):
        pid = next(iter(self.calls)); before = self.dataset.keywords[pid]
        out = copy.deepcopy(self.calls[pid]['parsed_output'])
        out['features']['gender'] = 'Women'
        with self.assertRaises(ValueError): validate_response(out, before)

    def test_outside_schema_only_without_other_and_requires_reason(self):
        pid = '2071147'; before = self.dataset.keywords[pid]
        out = copy.deepcopy(self.calls[pid]['parsed_output'])
        out['features']['pattern'] = 'outside_schema'
        out['outside_schema_reasons'] = {'pattern': 'Unusual pattern.'}
        with self.assertRaises(ValueError): validate_response(out, before)
        out = copy.deepcopy(self.calls[pid]['parsed_output'])
        out['features']['fit'] = 'outside_schema'
        with self.assertRaises(ValueError): validate_response(out, before)
        out['outside_schema_reasons'] = {'fit': 'The torso is obscured in every view.'}
        self.assertEqual(validate_response(out, before)['fit'], 'outside_schema')

    def test_product_problem_is_retained_and_cannot_enter_bank(self):
        pid = next(iter(self.calls))
        out = {'product_status': 'out_of_category', 'product_reason': 'The record depicts shoes.',
               'features': None, 'outside_schema_reasons': {}}
        result = self.dataset.result(pid, out, {'call_id': 'test'})
        self.assertEqual(result['status'], 'needs_review')
        self.assertEqual(result['features'], self.dataset.keywords[pid]['features'])
        self.dataset.add_reference(result)
        self.assertNotIn(pid, self.dataset.bank)

    def test_successful_product_can_extend_bank(self):
        result = next(iter(self.results.values()))
        size = len(self.dataset.bank)
        self.dataset.add_reference(result)
        self.assertEqual(len(self.dataset.bank), size + 1)
        self.dataset.bank.pop(result['product_id'])

    def test_missing_third_image_has_no_silent_fallback(self):
        with self.assertRaises(KeyError): example_images([{'pose': 'id_gridfs_1'}])

    def test_complete_product_without_third_image_is_not_added_to_bank(self):
        result = next(iter(self.results.values()))
        pid = result['product_id']
        original_images = self.dataset.images[pid]
        try:
            self.dataset.images[pid] = [im for im in original_images if im['pose'] != 'id_gridfs_3']
            self.assertFalse(self.dataset.add_reference(result))
            self.assertNotIn(pid, self.dataset.bank)
            self.assertEqual(result['status'], 'ready')
        finally:
            self.dataset.images[pid] = original_images


if __name__ == '__main__': unittest.main()
