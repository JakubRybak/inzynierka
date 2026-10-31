"""Regression checks for the supported Tops, Dresses and Skirts rules."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'scripts'))
from engine import assign, extract_product, load_config, read_yaml, validate_rule
from run_extraction import validate, write_output


class ExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, _ = load_config(BASE / 'config')

    def product(self, category='T-shirts', **updates):
        section = {c: s for s, c in self.config}[category]
        product = dict(product_id='test', section=section, category=category, name='Black product',
                       description='', gender='Men', brand='Example Brand', composition='100% cotton', original_category='')
        product.update(updates)
        return product

    def feature(self, category, feature, **updates):
        product = self.product(category, **updates)
        return assign(product, self.config[(product['section'], category)][feature], {})

    def test_supported_scope(self):
        self.assertEqual(set(self.config), {('Tops', 'T-shirts'), ('Tops', 'Polos'),
            ('Tops', 'Tank tops & Camisoles'), ('Tops', 'Bodysuits'), ('Dresses', 'Dresses'), ('Skirts', 'Skirts'),
            *[('Jackets & Coats', c) for c in ('Bombers', 'Classic Coats', 'Jackets', 'Trench Coats', 'Vests')],
            *[('Pants', c) for c in ('Cargo Pants', 'Jeans', 'Sweatpants & Lounge Pants', 'Trousers')],
            ('Shirts & Blouses', 'Shirts'), ('Shirts & Blouses', 'Blouses')})

    def test_lining_composition(self):
        cases = [('Body: 100% wool. Lining: 100% cupro.', '', 'assigned', {'Viscose': 100.0}),
                 ('100% wool.', 'Unlined. Tonal stitching.', 'assigned', 'Unlined'),
                 ('100% wool.', 'Fully lined.', 'assigned', 'Unknown'),
                 ('Body: 100% wool. Lining 1: 100% silk. Lining 2: 100% cupro.', '', 'assigned', 'Unknown'),
                 ('Body: 100% wool. Sleeve lining: 100% silk.', '', 'assigned', 'Unknown')]
        for composition, description, status, expected in cases:
            with self.subTest(composition=composition, description=description):
                value, actual, *_ = self.feature('Jackets', 'lining_composition', composition=composition,
                                                 description=description)
                self.assertEqual((value, actual), (expected, status))

    def test_default_value(self):
        self.assertEqual(self.feature('Jackets', 'fit', description='Oversized fit.')[:2], ('Oversized', 'assigned'))
        self.assertEqual(self.feature('Jackets', 'fit', description='Oversized lapels.')[:3], ('Regular', 'assigned', 'default'))

    def test_priority(self):
        self.assertEqual(self.feature('Jeans', 'distressing', description='Fading and distressing throughout.')[0], 'Distressed')
        self.assertEqual(self.feature('Jeans', 'distressing', description='Fading throughout.')[0], 'Faded')
        self.assertIsNone(self.feature('Jeans', 'distressing', description='Tonal stitching.')[0])

    def test_excluded_phrases(self):
        self.assertEqual(self.feature('Shirts', 'collar_type', description='Open spread collar.')[0], 'Camp Collar')
        self.assertIsNone(self.feature('Jackets', 'insulation', description='Fur-lined hood.')[0])
        self.assertEqual(self.feature('Jackets', 'insulation', description='Fur-lined body.')[0], 'Other')

    def test_colors(self):
        for title, expected in [('Black White Red', ['Multicolor']), ('Multicolor Black', ['Multicolor']),
                                ('Black White', ['Black', 'White']), ('Navy Blue', ['Blue']), ('Unknown', None)]:
            with self.subTest(title=title):
                self.assertEqual(self.feature('T-shirts', 'colors', name=title)[0], expected)
        self.assertEqual(self.feature('T-shirts', 'colors', name='White Black Label T-shirt', brand='Black Label')[0], ['White'])
        self.assertIsNone(self.feature('T-shirts', 'colors', name='Off-White T-shirt', brand='Off-White')[0])
        self.assertEqual(self.feature('T-shirts', 'colors', name='Off-White T-shirt', brand='Another Brand')[0], ['White'])

    def test_composition(self):
        cases = [('100% cotton', 'assigned', {'Cotton': 100.0}),
                 ('Body: 98% cotton, 2% elastane. Lining: 100% silk.', 'assigned', {'Cotton': 98.0, 'Elastane': 2.0}),
                 ('Body: 100% cotton. Body: 100% silk.', 'ambiguous_main_section', None),
                 ('Shell: 100% cotton.', 'assigned', {'Cotton': 100.0}),
                 ('Shell: 100% cotton. Body: 100% silk.', 'ambiguous_main_section', None),
                 ('Body: 100% cotton. Trim 1: 90% wool, 10% nylon.', 'assigned', {'Cotton': 100.0}),
                 ('90% cotton', 'sum_not_100', None), ('100% mystery', 'unmapped_material', None),
                 ('cotton', 'unparsed_composition', None), ('', 'undefined', None),
                 ('50% cotton, 50% coton', 'assigned', {'Cotton': 100.0})]
        for text, status, expected in cases:
            with self.subTest(text=text):
                value, actual, *_ = self.feature('T-shirts', 'main_composition', composition=text)
                self.assertEqual((value, actual), (expected, status))

    def test_unicode_section_boundaries(self):
        cases = [
            ('Main: 50% acetate, 50% viscose. Appliqué: 100% polyester.',
             {'Viscose': 100.0}, 'assigned'),
            ('Main: 50% acetate, 50% viscose. Appliqu�: 100% polyester.',
             {'Viscose': 100.0}, 'assigned'),
            ('Appliqu�: 100% polyester. Body: 100% cotton.',
             {'Cotton': 100.0}, 'assigned'),
            ('Main: 100% cotton. Applique\u0301: 100% polyester.',
             {'Cotton': 100.0}, 'assigned'),
            ('Ma�n: 100% cotton.', None, 'ambiguous_main_section'),
            ('Main: 90% cotton. Appliqu�: 100% polyester.', None, 'sum_not_100'),
            ('Main: 100% mystery. Appliqu�: 100% polyester.', None, 'unmapped_material'),
            ('Main: 100% cott�n. Appliqu�: 100% polyester.', None, 'unparsed_composition'),
            ('Main: 100% cotton. Body: 100% silk. Appliqu�: 100% polyester.',
             None, 'ambiguous_main_section'),
        ]
        for text, expected, status in cases:
            with self.subTest(text=text):
                value, actual_status, *_ = self.feature('T-shirts', 'main_composition', composition=text)
                self.assertEqual((value, actual_status), (expected, status))

    def test_pattern_is_always_deferred_to_llm(self):
        for (_, category), rules in self.config.items():
            with self.subTest(category=category):
                result = self.feature(category, 'pattern', name='Striped floral product',
                                      description='Solid color. Logo print. Camouflage throughout.')
                self.assertEqual(result, (None, 'undefined', None, {}))
                self.assertEqual(rules['pattern']['strategy'], 'llm')

    def test_sleeveless_tshirts_and_polos(self):
        for category in ['T-shirts', 'Polos']:
            with self.subTest(category=category):
                self.assertEqual(self.feature(category, 'sleeve_length', description='Sleeveless top.')[0], 'Sleeveless')
                self.assertEqual(self.feature(category, 'sleeve_length', name='Sleeveless top',
                                              description='Long sleeve top.')[1], 'undefined')

    def test_three_quarter_sleeves(self):
        for category in ['T-shirts', 'Polos', 'Bodysuits', 'Dresses']:
            for text in ['three-quarter sleeve', 'three-quarter sleeves',
                         'three-quarter length sleeves', '3/4 sleeve', '3/4 sleeves',
                         'cropped sleeve', 'cropped sleeves', 'cropped-sleeve']:
                with self.subTest(category=category, text=text):
                    self.assertEqual(self.feature(category, 'sleeve_length',
                                                  description=text)[0], 'Three-Quarter Sleeve')
            with self.subTest(category=category, conflict=True):
                self.assertEqual(self.feature(category, 'sleeve_length', name='Long sleeve top',
                                              description='3/4 sleeves.')[1], 'undefined')

    def test_neckline_conflict(self):
        for category in ['T-shirts', 'Bodysuits', 'Tank tops & Camisoles', 'Dresses']:
            with self.subTest(category=category):
                value, status, *_ = self.feature(category, 'neckline', name='V-neck product', description='Crewneck collar.')
                self.assertEqual((value, status), (None, 'undefined'))
                self.assertEqual(self.feature(category, 'neckline', description='Boat neck.')[0], 'Other')

    def test_fit_conflict(self):
        for category in ['T-shirts', 'Polos', 'Tank tops & Camisoles']:
            self.assertIsNone(self.feature(category, 'fit', description='Slim-fit and relaxed-fit.')[0])
            self.assertEqual(self.feature(category, 'fit', description='Relaxed-fit.')[0], 'Oversized')

    def test_dress_exclusion_is_local(self):
        for description, expected in [('T-shirt dress.', ['T-Shirt Dress']),
                                      ('Shirtdress.', ['Shirt Dress']),
                                      ('T-shirt dress and a separate shirt dress.', ['Shirt Dress', 'T-Shirt Dress'])]:
            self.assertEqual(self.feature('Dresses', 'dress_type', description=description)[0], expected)

    def test_source_lengths(self):
        for category, noun in [('Dresses', 'DRESSES'), ('Skirts', 'SKIRTS')]:
            self.assertEqual(self.feature(category, 'length', original_category='LONG ' + noun)[0], 'Maxi')
            product = self.product(category, name='Mini product', original_category='UNKNOWN')
            result = extract_product(product, self.config[(product['section'], category)])
            self.assertEqual(result['status'], 'excluded')
            self.assertNotIn('length', result['features'])

    def test_strap_dependencies(self):
        for category in ['Bodysuits', 'Tank tops & Camisoles', 'Dresses']:
            product = self.product(category, description='Strapless top.', original_category='SHORT DRESSES')
            result = extract_product(product, self.config[(product['section'], category)])
            self.assertEqual(result['features']['strap_width'], 'Not Applicable')
            rule = self.config[(product['section'], category)]['strap_width']
            self.assertEqual(assign(product, rule, {'strap_style': 'Strapless'})[0], 'Not Applicable')
            if category != 'Tank tops & Camisoles':
                self.assertEqual(assign(product, rule, {'strap_style': 'Standard Sleeved'})[0], 'Not Applicable')

    def test_skirt_multi(self):
        self.assertEqual(self.feature('Skirts', 'skirt_type', description='Pleated skirt with wrap construction.')[0], ['Pleated', 'Wrap'])

    def test_excluded_retained_and_ready(self):
        product = self.product(composition='90% cotton')
        original = copy.deepcopy(product)
        record = extract_product(product, self.config[('Tops', 'T-shirts')])
        self.assertEqual(product, original)
        self.assertEqual(record['status'], 'excluded')
        self.assertEqual(record['features']['colors'], ['Black'])
        validate([record], self.config)
        with tempfile.TemporaryDirectory() as tmp:
            write_output(Path(tmp), 'train', [record])
            self.assertEqual(json.loads((Path(tmp) / 'products_train.jsonl').read_text()), record)
        polo = self.product('Polos', description='Solid color. Short sleeves. Slim-fit.')
        result = extract_product(polo, self.config[('Tops', 'Polos')])
        self.assertEqual(result['status'], 'pending')
        self.assertNotIn('pattern', result['features'])
        polo['gender'] = ''
        self.assertEqual(extract_product(polo, self.config[('Tops', 'Polos')])['status'], 'excluded')

    def test_brand_is_top_level_and_required(self):
        rules = self.config[('Tops', 'T-shirts')]
        product = self.product(brand='Example Brand')
        record = extract_product(product, rules)
        self.assertEqual(record['brand'], 'Example Brand')
        self.assertNotIn('brand', record['features'])
        self.assertNotIn('brand', record['feature_metadata'])
        self.assertNotIn({'feature': 'brand', 'reason': 'empty'}, record['exclusion_reasons'])

        product['brand'] = '  '
        record = extract_product(product, rules)
        self.assertEqual(record['brand'], '  ')
        self.assertEqual(record['status'], 'excluded')
        self.assertIn({'feature': 'brand', 'reason': 'empty'}, record['exclusion_reasons'])
        validate([record], self.config)

    def test_bad_config_rejected(self):
        for rule in [{'strategy': 'typo'}, {'strategy': 'single', 'colums': ['name']}]:
            with self.assertRaises(ValueError):
                validate_rule('test', rule, {})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.yaml'
            path.write_text('value: 1\nvalue: 2\n')
            with self.assertRaises(ValueError):
                read_yaml(path)


if __name__ == '__main__':
    unittest.main()
