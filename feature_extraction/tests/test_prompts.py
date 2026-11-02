"""Dynamic blocks and output fields must follow exactly the unresolved features."""
import json
import unittest

from feature_extraction.keywords.engine import extract_product
from feature_extraction.llm.prompt_builder import CONFIGS, build_prompt, requested_rules
from feature_extraction.llm.validation import validate_response


class PromptTests(unittest.TestCase):
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
