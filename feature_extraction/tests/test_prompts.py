"""Dynamic blocks and output fields must follow exactly the unresolved features."""
import json
import copy
import unittest
from unittest.mock import patch

from feature_extraction.keywords.engine import extract_product
from feature_extraction.llm import prompt_builder
from feature_extraction.llm.prompt_builder import CONFIGS, build_prompt, requested_rules
from feature_extraction.llm.validation import validate_response


class PromptTests(unittest.TestCase):
    def neckline_prompt(self, category):
        section = 'Dresses' if category == 'Dresses' else 'Tops'
        source = dict(product_id='target', name='Black product', description='', brand='Brand',
                      section=section, category=category, gender='Women', composition='100% cotton',
                      original_category='SHORT DRESSES')
        record = extract_product(source, CONFIGS[(section, category)])
        labels = {key: record['features'].get(key, 'Other') for key in CONFIGS[(section, category)]}
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
                record = extract_product(source, CONFIGS[(section, category)])
                # All supported categories expose these fields; sleeve length is locked where applicable.
                if 'sleeve_length' in CONFIGS[(section, category)]:
                    record['features']['sleeve_length'] = 'Short Sleeve'
                missing = requested_rules(record)
                labels = {key: record['features'].get(key, 'Other') for key in CONFIGS[(section, category)]}
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
        record = extract_product(source, CONFIGS[('Tops', 'T-shirts')])
        with self.assertRaises(ValueError):
            validate_response({'product_status': 'ok', 'product_reason': '',
                               'features': {'gender': 'Women'}, 'outside_schema_reasons': {}}, record)


if __name__ == '__main__':
    unittest.main()
