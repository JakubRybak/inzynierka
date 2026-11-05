"""Dynamic blocks and output fields must follow exactly the unresolved features."""
import json
import copy
import unittest
from unittest.mock import patch

from feature_extraction.keywords.engine import extract_product, load_config
from feature_extraction.settings import BASE
from feature_extraction.llm import prompt_builder
from feature_extraction.llm.prompt_builder import SCHEMAS, build_prompt, requested_features, choices, is_multi_value
from feature_extraction.llm.validation import validate_response


KEYWORDS, _ = load_config(BASE / 'keywords/definitions', SCHEMAS)


class PromptTests(unittest.TestCase):
    def category_case(self, category):
        section = next(section for section, name in SCHEMAS if name == category)
        source = dict(product_id='target', name='Product', description='', brand='Brand',
                      section=section, category=category, gender='Women', composition='100% cotton',
                      original_category='SHORT SKIRTS' if category == 'Skirts' else 'SHORT DRESSES')
        record = extract_product(source, KEYWORDS[(section, category)], SCHEMAS[(section, category)])
        missing = requested_features(record)
        features = {}
        for feature, rule in missing.items():
            allowed = choices(category, feature, rule)
            value = 'Other' if 'Other' in allowed else allowed[0]
            features[feature] = [value] if is_multi_value(rule) else value
        labels = {**record['features'], **features}
        examples = [{'record': {**record, 'product_id': str(i), 'features': labels, 'status': 'ready'},
                     'source': source, 'images': []} for i in range(2)]
        prompt = build_prompt(record, source, [], examples)
        response = {'product_status': 'ok', 'product_reason': '', 'features': features}
        if 'outside_schema_reasons' in prompt['generation_config']['responseSchema']['properties']:
            response['outside_schema_reasons'] = {}
        return record, prompt, response

    def test_all_supported_categories_have_complete_llm_definitions_and_valid_outputs(self):
        for category in prompt_builder.DEFINITIONS:
            with self.subTest(category=category):
                record, prompt, response = self.category_case(category)
                requested = set(requested_features(record))
                schema = prompt['generation_config']['responseSchema']['properties']['features']['properties']
                self.assertEqual(set(schema), requested)
                self.assertEqual(set(prompt_builder.category_definitions(category)), requested)
                merged = validate_response(response, record)
                self.assertEqual(set(merged), set(SCHEMAS[(record['section'], category)]))
                for key, value in record['features'].items():
                    self.assertEqual(merged[key], value)
                for part in prompt['parts']:
                    if part.get('text', '').startswith(('REFERENCE 1\n', 'REFERENCE 2\n')):
                        labels = json.loads(part['text'].split('\n', 1)[1])['labels']
                        self.assertEqual(set(labels), requested)
                if category in ('Dresses', 'Skirts'):
                    self.assertNotIn('length', schema)

    def test_shared_features_have_consistent_definitions(self):
        definitions = {category: prompt_builder.category_definitions(category)
                       for category in prompt_builder.DEFINITIONS}
        for category in ['Polos', 'Bodysuits']:
            for feature in ['colors', 'pattern', 'sleeve_length']:
                self.assertEqual(definitions[category][feature], definitions['T-shirts'][feature])
        self.assertEqual(definitions['Polos']['fit'], definitions['T-shirts']['fit'])
        self.assertEqual(definitions['Bodysuits']['neckline'], definitions['T-shirts']['neckline'])
        for feature in ['strap_style', 'strap_width']:
            self.assertEqual(definitions['Bodysuits'][feature], definitions['Dresses'][feature])
        self.assertEqual(definitions['Skirts']['colors'], definitions['T-shirts']['colors'])
        self.assertEqual(definitions['Skirts']['pattern']['values'], definitions['T-shirts']['pattern']['values'])

    def test_matching_features_keep_the_same_wording_across_categories(self):
        definitions = prompt_builder.DEFINITIONS
        for category in ['Cargo Pants', 'Sweatpants & Lounge Pants', 'Jeans']:
            for feature in ['fit', 'leg_shape', 'length', 'rise', 'waistband_type', 'cuff_style']:
                self.assertEqual(definitions[category][feature], definitions['Trousers'][feature])
        for feature in ['fit', 'rise', 'waistband_type']:
            self.assertEqual(definitions['Shorts'][feature], definitions['Trousers'][feature])
        self.assertEqual(definitions['Trousers']['rise']['values'], definitions['Skirts']['rise']['values'])
        for category in ['Shirts', 'Blouses']:
            for feature in ['sleeve_length', 'fit']:
                self.assertEqual(definitions[category][feature], definitions['T-shirts'][feature])
        self.assertEqual(definitions['Shirts']['length'], definitions['Blouses']['length'])
        self.assertEqual(definitions['Blouses']['neckline'], definitions['Dresses']['neckline'])
        for feature in ['hood', 'closure_type', 'insulation']:
            for category in ['Trench Coats', 'Jackets', 'Bombers', 'Vests']:
                self.assertEqual(definitions[category][feature], definitions['Classic Coats'][feature])
        for category in ['Trench Coats', 'Jackets']:
            self.assertEqual(definitions[category]['collar_type'], definitions['Classic Coats']['collar_type'])
        self.assertEqual(definitions['Trench Coats']['length'], definitions['Classic Coats']['length'])
        for category in ['Bombers', 'Vests']:
            self.assertEqual(definitions[category]['length'], definitions['Jackets']['length'])

    def test_composition_is_sent_only_when_insulation_is_requested(self):
        def payloads(category):
            _, prompt, _ = self.category_case(category)
            return [json.loads(part['text'].split('\n', 1)[1]) for part in prompt['parts']
                    if part.get('text', '').startswith(('TARGET PRODUCT\n', 'REFERENCE 1\n', 'REFERENCE 2\n'))]
        self.assertEqual([payload['composition'] for payload in payloads('Jackets')], ['100% cotton'] * 3)
        self.assertTrue(all('composition' not in payload for payload in payloads('Trousers')))

    def test_common_pattern_is_used_by_every_category(self):
        common = copy.deepcopy(prompt_builder.COMMON_DEFINITIONS)
        common['pattern']['instruction'] = 'Shared pattern instruction.'
        with patch.object(prompt_builder, 'COMMON_DEFINITIONS', common):
            for category in prompt_builder.DEFINITIONS:
                with self.subTest(category=category):
                    _, prompt, _ = self.category_case(category)
                    self.assertIn('Shared pattern instruction.', prompt['parts'][0]['text'])
                    self.assertNotIn('pattern', prompt_builder.DEFINITIONS[category])
                    self.assertNotIn('colors', prompt_builder.DEFINITIONS[category])

    def test_category_definition_overrides_the_common_feature(self):
        common = copy.deepcopy(prompt_builder.COMMON_DEFINITIONS)
        common['pattern']['instruction'] = 'Shared pattern instruction.'
        categories = copy.deepcopy(prompt_builder.DEFINITIONS)
        categories['T-shirts']['pattern'] = copy.deepcopy(common['pattern'])
        categories['T-shirts']['pattern']['instruction'] = 'Category pattern instruction.'
        with patch.object(prompt_builder, 'COMMON_DEFINITIONS', common), \
             patch.object(prompt_builder, 'DEFINITIONS', categories):
            _, tshirt, _ = self.category_case('T-shirts')
            _, dress, _ = self.category_case('Dresses')
            self.assertIn('Category pattern instruction.', tshirt['parts'][0]['text'])
            self.assertNotIn('Shared pattern instruction.', tshirt['parts'][0]['text'])
            self.assertIn('Shared pattern instruction.', dress['parts'][0]['text'])

    def test_skirt_type_accepts_multiple_values_and_other_alone(self):
        record, prompt, response = self.category_case('Skirts')
        schema = prompt['generation_config']['responseSchema']['properties']['features']['properties']
        self.assertEqual(schema['skirt_type']['type'], 'ARRAY')
        self.assertEqual(schema['skirt_type']['maxItems'], 5)
        for value in [['Pleated', 'Asymmetric'], ['Wrap', 'Tiered', 'Ruffled'], ['Other']]:
            with self.subTest(value=value):
                response['features']['skirt_type'] = value
                self.assertEqual(validate_response(response, record)['skirt_type'], value)
        for value in ['Pleated', [], ['Pleated', 'Pleated'], ['Other', 'Wrap'], ['outside_schema'], 'outside_schema']:
            with self.subTest(invalid=value):
                response['features']['skirt_type'] = value
                with self.assertRaises(ValueError):
                    validate_response(response, record)

    def test_skirt_rise_can_report_outside_schema_with_reason(self):
        record, _, response = self.category_case('Skirts')
        response['features']['rise'] = 'outside_schema'
        with self.assertRaises(ValueError):
            validate_response(response, record)
        response['outside_schema_reasons'] = {'rise': 'The waistband is hidden in every view.'}
        self.assertEqual(validate_response(response, record)['rise'], 'outside_schema')

    def test_bodysuit_strap_dependency_includes_standard_sleeved(self):
        record, prompt, response = self.category_case('Bodysuits')
        self.assertIn('strap_style is Strapless or Standard Sleeved.', prompt['parts'][0]['text'])
        for style in ['Strapless', 'Standard Sleeved']:
            response['features'].update(strap_style=style, strap_width='Not Applicable')
            self.assertEqual(validate_response(response, record)['strap_width'], 'Not Applicable')
            response['features']['strap_width'] = 'Wide'
            with self.assertRaises(ValueError):
                validate_response(response, record)

    def neckline_prompt(self, category):
        section = 'Dresses' if category == 'Dresses' else 'Tops'
        source = dict(product_id='target', name='Black product', description='', brand='Brand',
                      section=section, category=category, gender='Women', composition='100% cotton',
                      original_category='SHORT DRESSES')
        record = extract_product(source, KEYWORDS[(section, category)], SCHEMAS[(section, category)])
        labels = {key: record['features'].get(key, 'Other') for key in SCHEMAS[(section, category)]}
        examples = [{'record': {**record, 'product_id': str(i), 'features': labels, 'status': 'ready'},
                     'source': source, 'images': []} for i in range(2)]
        return build_prompt(record, source, [], examples)

    def test_editing_tshirt_definition_does_not_change_other_categories(self):
        before = {category: self.neckline_prompt(category) for category in
                  ['T-shirts', 'Dresses', 'Tank tops & Camisoles']}
        definitions = copy.deepcopy(prompt_builder.DEFINITIONS)
        definitions['T-shirts']['neckline']['instruction'] = 'T-shirt neckline instruction.'
        definitions['T-shirts']['neckline']['values']['Crewneck'] = 'T-shirt crewneck description.'
        with patch.object(prompt_builder, 'DEFINITIONS', definitions):
            tshirt = self.neckline_prompt('T-shirts')
            self.assertIn('T-shirt neckline instruction.', tshirt['parts'][0]['text'])
            self.assertIn('T-shirt crewneck description.', tshirt['parts'][0]['text'])
            self.assertNotEqual(tshirt, before['T-shirts'])
            for category in ['Dresses', 'Tank tops & Camisoles']:
                self.assertEqual(self.neckline_prompt(category), before[category])

    def test_missing_category_definition_has_no_shared_fallback(self):
        definitions = copy.deepcopy(prompt_builder.DEFINITIONS)
        del definitions['Dresses']
        with patch.object(prompt_builder, 'DEFINITIONS', definitions):
            with self.assertRaisesRegex(ValueError, 'No LLM feature definitions for category: Dresses'):
                self.neckline_prompt('Dresses')

    def test_category_values_are_used_by_prompt_and_response_schema(self):
        for category, collared in [('T-shirts', False), ('Dresses', True)]:
            prompt = self.neckline_prompt(category)
            text = prompt['parts'][0]['text']
            schema = prompt['generation_config']['responseSchema']['properties']['features']['properties']
            self.assertEqual('Collared' in schema['neckline']['enum'], collared)
            self.assertEqual('- Collared:' in text, collared)

    def test_assigned_features_are_omitted_in_all_three_categories(self):
        for section, category in [('Tops', 'T-shirts'), ('Dresses', 'Dresses'), ('Tops', 'Tank tops & Camisoles')]:
            with self.subTest(category=category):
                source = dict(product_id='target', name='Black product', description='', brand='Brand',
                              section=section, category=category, gender='Women', composition='100% cotton',
                              original_category='SHORT DRESSES')
                record = extract_product(source, KEYWORDS[(section, category)], SCHEMAS[(section, category)])
                # All supported categories expose these fields; sleeve length is locked where applicable.
                if 'sleeve_length' in SCHEMAS[(section, category)]:
                    record['features']['sleeve_length'] = 'Short Sleeve'
                missing = requested_features(record)
                labels = {key: record['features'].get(key, 'Other') for key in SCHEMAS[(section, category)]}
                references = [{'record': {**record, 'product_id': str(i), 'features': labels, 'status': 'ready'},
                               'source': source, 'images': []} for i in range(2)]
                prompt = build_prompt(record, source, [], references)
                fields = prompt['generation_config']['responseSchema']['properties']['features']['properties']
                self.assertEqual(set(fields), set(missing))
                for part in prompt['parts']:
                    if part.get('text', '').startswith(('REFERENCE 1\n', 'REFERENCE 2\n')):
                        shown = json.loads(part['text'].split('\n', 1)[1])['labels']
                        self.assertEqual(set(shown), set(missing))
                        self.assertNotIn('sleeve_length', shown)
                definitions = prompt['parts'][0]['text']
                self.assertNotIn('\nsleeve_length\n', definitions)
                if category == 'Dresses':
                    self.assertNotIn('length', fields)

    def test_keywords_cannot_be_overwritten_by_extra_output_fields(self):
        source = dict(product_id='1', name='Black tee', description='', brand='Brand', section='Tops',
                      category='T-shirts', gender='Men', composition='100% cotton')
        record = extract_product(source, KEYWORDS[('Tops', 'T-shirts')], SCHEMAS[('Tops', 'T-shirts')])
        with self.assertRaises(ValueError):
            validate_response({'product_status': 'ok', 'product_reason': '',
                               'features': {'gender': 'Women'}, 'outside_schema_reasons': {}}, record)


if __name__ == '__main__':
    unittest.main()
