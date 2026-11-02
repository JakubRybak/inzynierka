"""Validate complete keyword extraction records."""
from .engine import allowed_values

def validate(records, configs):
    assert len({r['product_id'] for r in records}) == len(records)
    for record in records:
        assert isinstance(record['brand'], str)
        brand_missing = not record['brand'].strip()
        assert brand_missing == any(reason == {'feature': 'brand', 'reason': 'empty'}
                                    for reason in record['exclusion_reasons'])
        rules = configs[(record['section'], record['category'])]
        assert set(record['feature_metadata']) == set(rules)
        for feature, meta in record['feature_metadata'].items():
            assert (feature in record['features']) == (meta['status'] == 'assigned')
            if feature in record['features']:
                value = record['features'][feature]
                assert value is not None and value != []
                values = set(value) if isinstance(value, (list, dict)) else {value}
                assert values <= allowed_values(rules[feature]), (feature, value)
        assert (record['status'] == 'excluded') == bool(record['exclusion_reasons'])
        assert record['status'] != 'ready' or len(record['features']) == len(rules)
        if 'colors' in record['features']:
            colors = record['features']['colors']
            rule = rules['colors']
            assert len(colors) <= rule['max_named_colors']
            assert rule['multicolor_value'] not in colors or colors == [rule['multicolor_value']]
        if 'main_composition' in record['features']:
            rule = rules['main_composition']
            assert abs(sum(record['features']['main_composition'].values()) - rule['total']) <= rule['tolerance']
        for feature, rule in rules.items():
            if 'derive' in rule and record['features'].get(rule['derive']['feature']) in rule['derive']['in']:
                assert record['features'][feature] == rule['derive']['value']
