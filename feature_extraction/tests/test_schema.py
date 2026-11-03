"""Contracts must remain independent of keyword strategies and model responses."""
import copy
import unittest
from unittest.mock import patch

from feature_extraction.config_io import read_yaml
from feature_extraction.keywords.engine import assign, extract_product, load_config, validate_rule
from feature_extraction.llm import prompt_builder
from feature_extraction.llm.validation import validate_response
from feature_extraction.schema import load_schemas
from feature_extraction.schema.loader import validate_definition
from feature_extraction.settings import BASE
from feature_extraction.validation import validate_features, validate_value


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas, _ = load_schemas()
        cls.keywords, _ = load_config(BASE / 'keywords/definitions', cls.schemas)

    def test_llm_only_features_have_no_keyword_rules(self):
        for key, schema in self.schemas.items():
            self.assertNotIn('pattern', self.keywords[key])
            self.assertEqual(schema['pattern']['type'], 'single_choice')
            if key[0] == 'Jackets & Coats':
                self.assertNotIn('closure_type', self.keywords[key])
                self.assertNotIn('length', self.keywords[key])
                self.assertEqual(schema['closure_type']['type'], 'multi_choice')
        for path in (BASE / 'keywords/definitions').rglob('*.yaml'):
            self.assertNotIn('strategy: llm', path.read_text())

    def test_keyword_rules_cannot_redefine_values_or_cardinality(self):
        definition = self.schemas[('Tops', 'T-shirts')]['neckline']
        original = self.keywords[('Tops', 'T-shirts')]['neckline']
        for field, value in [('allowed_values', ['Crewneck']), ('type', 'multi_choice'),
                             ('exclusive_values', ['Other'])]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_rule('neckline', {**original, field: value}, definition)
        invalid = copy.deepcopy(original)
        invalid['keywords']['Invented'] = ['invented']
        with self.assertRaises(ValueError):
            validate_rule('neckline', invalid, definition)
        with self.assertRaises(ValueError):
            validate_rule('neckline', {'strategy': 'llm'}, definition)
        invalid['keywords'] = {'Crewneck': []}
        with self.assertRaises(ValueError):
            validate_rule('neckline', invalid, definition)

    def test_cardinality_change_needs_only_schema_not_keyword_changes(self):
        pattern = copy.deepcopy(self.schemas[('Tops', 'T-shirts')]['pattern'])
        before = prompt_builder.build_schema({'pattern': pattern}, 'T-shirts')
        pattern.update(type='multi_choice', max_items=2, exclusive_values=['Other'])
        validate_definition('pattern', pattern, {})
        after = prompt_builder.build_schema({'pattern': pattern}, 'T-shirts')
        self.assertEqual(before['properties']['features']['properties']['pattern']['type'], 'STRING')
        self.assertEqual(after['properties']['features']['properties']['pattern']['type'], 'ARRAY')
        validate_value(['Striped', 'Floral'], pattern)
        with self.assertRaises(ValueError):
            validate_value(['Striped', 'Other'], pattern)

    def test_missing_rules_still_produce_complete_metadata(self):
        key = 'Tops', 'T-shirts'
        product = dict(product_id='target', section=key[0], category=key[1], brand='Brand')
        result = extract_product(product, {}, self.schemas[key])
        self.assertEqual(set(result['feature_metadata']), set(self.schemas[key]))
        self.assertEqual(result['status'], 'excluded')  # Required source data is still enforced.
        self.assertEqual(result['feature_metadata']['pattern'],
                         {'status': 'undefined', 'source': None, 'strategy': None, 'evidence': {}})

    def test_lining_supports_composition_and_special_values(self):
        definition = self.schemas[('Jackets & Coats', 'Jackets')]['lining_composition']
        for value in [{'Cotton': 60, 'Silk': 40}, 'Unlined', 'Unknown']:
            validate_value(value, definition)
        for value in [{'Cotton': 90}, {'Unknown': 100}, {}, {'Cotton': float('nan')}, 'Cotton']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_value(value, definition)

    def test_dependency_is_generic_and_bidirectional(self):
        schema = {
            'construction': {'type': 'single_choice', 'values': ['None', 'Present']},
            'width': {'type': 'single_choice', 'values': ['Wide', 'Not Applicable'],
                      'value_dependency': {'feature': 'construction', 'in': ['None'], 'value': 'Not Applicable'}}}
        self.assertEqual(assign({}, None, {'construction': 'None'}, schema['width'])[:3],
                         ('Not Applicable', 'assigned', 'derived_rule'))
        for features in [{'construction': 'None', 'width': 'Not Applicable'},
                         {'construction': 'Present', 'width': 'Wide'}]:
            validate_features(features, schema, complete=True)
        for features in [{'construction': 'None', 'width': 'Wide'},
                         {'construction': 'Present', 'width': 'Not Applicable'}]:
            with self.assertRaises(ValueError):
                validate_features(features, schema, complete=True)

    def test_closure_type_response_uses_schema_without_keyword_rule(self):
        key = 'Jackets & Coats', 'Jackets'
        schema = self.schemas[key]
        labels = {}
        for feature, definition in schema.items():
            if definition['type'] == 'composition':
                value = {'Cotton': 100}
            elif definition['type'] == 'multi_choice':
                value = [definition['values'][0]]
            else:
                value = definition['values'][0]
            labels[feature] = value
        labels.pop('closure_type')
        record = {'section': key[0], 'category': key[1], 'features': labels,
                  'status': 'pending', 'exclusion_reasons': []}
        definitions = {**prompt_builder.DEFINITIONS, key[1]: {
            'closure_type': {'instruction': 'Choose the front closures.',
                             'values': {v: v for v in schema['closure_type']['values']}}}}
        with patch.object(prompt_builder, 'DEFINITIONS', definitions):
            requested = prompt_builder.requested_features(record)
            fields = prompt_builder.build_schema(requested, key[1])['properties']['features']['properties']
            self.assertEqual(fields['closure_type']['type'], 'ARRAY')
            response = {'product_status': 'ok', 'product_reason': '', 'features': {'closure_type': ['Zip', 'Button']}}
            self.assertEqual(validate_response(response, record)['closure_type'], ['Zip', 'Button'])
            for value in [['Other', 'Zip'], ['Open Front', 'Button'], 'Zip', ['Zip', 'Zip']]:
                response['features']['closure_type'] = value
                with self.subTest(value=value), self.assertRaises(ValueError):
                    validate_response(response, record)
            response['features'] = None
            with self.assertRaises(ValueError):
                validate_response(response, record)

    def test_invalid_contracts_are_rejected(self):
        for definition in [
                {'type': 'single_choice', 'values': ['A', 'A']},
                {'type': 'multi_choice', 'values': ['A'], 'max_items': 0},
                {'type': 'multi_choice', 'values': ['A'], 'max_items': 1, 'exclusive_values': ['B']},
                {'type': 'composition', 'values': ['Cotton'], 'total': 100, 'tolerance': -1}]:
            with self.subTest(definition=definition), self.assertRaises(ValueError):
                validate_definition('test', definition, {})


if __name__ == '__main__':
    unittest.main()
