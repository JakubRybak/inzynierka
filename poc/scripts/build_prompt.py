"""Build offline Gemini prompt previews and dynamic responseSchema; no API calls."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'extraction/scripts'))
from engine import allowed_values, load_config

PROMPTS = ROOT / 'poc/feature_extraction/prompts'
DEFINITIONS = json.loads((PROMPTS / 'feature_definitions.json').read_text())
CONFIGS, _ = load_config(ROOT / 'extraction/config')


def obj(properties, required=None):
    return {'type': 'OBJECT', 'properties': properties,
            'required': list(properties) if required is None else required,
            'propertyOrdering': list(properties)}


def enum(values):
    return {'type': 'STRING', 'enum': values}


def requested_rules(record):
    rules = CONFIGS[(record['section'], record['category'])]
    if record['status'] == 'excluded' or record['exclusion_reasons']:
        raise ValueError('Excluded products must not be submitted')
    missing = {k: v for k, v in rules.items() if k not in record['features']}
    if set(missing) - set(DEFINITIONS):
        raise ValueError(f'Unsupported LLM features: {set(missing) - set(DEFINITIONS)}')
    return missing


def choices(feature, rule):
    allowed = allowed_values(rule)
    values = [v for v in DEFINITIONS[feature]['values'] if v in allowed]
    if set(values) != allowed:
        raise ValueError(f'Definition/taxonomy mismatch: {feature}')
    return values


def build_schema(rules):
    fields, reasons = {}, {}
    for feature, rule in rules.items():
        values = choices(feature, rule)
        has_other = 'Other' in values
        if feature in ('colors', 'dress_type'):
            value_schema = {'type': 'ARRAY', 'items': enum(values), 'minItems': 1,
                            'maxItems': 2 if feature == 'colors' else len(values) - 1}
            if not has_other:
                value_schema = {'anyOf': [value_schema, enum(['outside_schema'])]}
        else:
            value_schema = enum(values if has_other else values + ['outside_schema'])
        fields[feature] = value_schema
        if not has_other:
            reasons[feature] = {'type': 'STRING', 'description': 'One factual sentence; present only if this feature is outside_schema.'}
    features = obj(fields)
    features['nullable'] = True
    features['description'] = 'Complete requested values when ok; null only for a product-level problem.'
    properties = {
        'product_status': enum(['ok', 'out_of_category', 'unusable_product']),
        'product_reason': {'type': 'STRING', 'description': 'Empty when ok; otherwise one short factual sentence.'},
        'features': features,
    }
    if reasons:
        properties['outside_schema_reasons'] = obj(reasons, required=[])
    return obj(properties)


def build_prompt(record, source, images, examples):
    rules = requested_rules(record)
    if not rules:
        raise ValueError('No unresolved features; skip this product')
    if len(examples) != 2 or len({e['record']['product_id'] for e in examples}) != 2:
        raise ValueError('Exactly two distinct references are required')
    for example in examples:
        ref = example['record']
        if (ref['product_id'] == record['product_id'] or ref['status'] != 'ready'
                or ref['category'] != record['category']
                or ref['features']['gender'] != record['features']['gender']):
            raise ValueError('Reference must be complete, different, same category and gender')
    definition_lines = ['REQUESTED FEATURES']
    for feature, rule in rules.items():
        definition_lines.extend(['', feature, DEFINITIONS[feature]['instruction']])
        for value in choices(feature, rule):
            definition_lines.append(f"- {value}: {DEFINITIONS[feature]['values'][value]}")
        definition_lines.append('Other is available: only the listed values are allowed.'
                                if 'Other' in choices(feature, rule)
                                else 'Other is unavailable: outside_schema is permitted under the decision rules.')
    # Show this relation only when BOTH features are requested. Otherwise validate
    # it locally after merging, without disclosing a locked value or its definition.
    if 'strap_style' in rules and 'strap_width' in rules:
        styles = ['Strapless']
        if 'Standard Sleeved' in choices('strap_style', rules['strap_style']):
            styles.append('Standard Sleeved')
        definition_lines.extend(['', 'JOINT CONSTRAINT',
            'strap_width must equal Not Applicable if and only if strap_style is ' + ' or '.join(styles) + '.'])
    parts = [{'text': '\n'.join(definition_lines)}, {'text':
        'The following two reference products illustrate the requested labels. '
        'They are not the target. Their labels are examples, not predictions for the target.'}]
    for i, example in enumerate(examples, 1):
        ref = example['record']; raw = example['source']
        payload = {'name': raw['name'], 'description': raw['description'],
                   'labels': {key: ref['features'][key] for key in rules}}
        parts.append({'text': f'REFERENCE {i}\n' + json.dumps(payload, ensure_ascii=False)})
        for img in example['images']:
            parts.extend([{'text': f'REFERENCE {i} IMAGE'}, {'local_image_path': img}])
    parts.append({'text': 'TARGET PRODUCT\n' + json.dumps({
        'category': record['category'], 'name': source['name'],
        'description': source['description'],
    }, ensure_ascii=False)})
    for img in images:
        parts.extend([{'text': 'TARGET IMAGE'}, {'local_image_path': img}])
    parts.append({'text': 'Classify the TARGET PRODUCT using only the requested features.'})
    return {
        'system_instruction': (PROMPTS / 'system.txt').read_text(),
        'parts': parts,
        'generation_config': {
            'responseMimeType': 'application/json', 'responseSchema': build_schema(rules),
            'thinkingConfig': {'thinkingLevel': 'MEDIUM'},
            'mediaResolution': 'MEDIA_RESOLUTION_MEDIUM',
        },
    }


def validate_response(response, record):
    """Business validation beyond server schema; does not mutate keyword values."""
    rules = requested_rules(record)
    reason_field = any('Other' not in choices(f, rule) for f, rule in rules.items())
    expected = {'product_status', 'product_reason', 'features'}
    if reason_field:
        expected.add('outside_schema_reasons')
    if set(response) != expected:
        raise ValueError('Unexpected response keys')
    status = response['product_status']; reason = response['product_reason']
    features = response['features']; reasons = response.get('outside_schema_reasons', {})
    if not isinstance(reason, str) or not isinstance(reasons, dict):
        raise ValueError('Invalid reason types')
    if status in ('out_of_category', 'unusable_product'):
        if not reason.strip() or features is not None or reasons:
            raise ValueError('Invalid product problem response')
        return None
    if status != 'ok' or reason != '' or not isinstance(features, dict) or set(features) != set(rules):
        raise ValueError('Expected exactly the missing features for an ok product')
    outside = set()
    for feature, value in features.items():
        values = choices(feature, rules[feature])
        if value == 'outside_schema':
            if 'Other' in values:
                raise ValueError('outside_schema forbidden when Other exists')
            outside.add(feature)
            continue
        if feature in ('colors', 'dress_type'):
            if not isinstance(value, list) or not value or not all(isinstance(x, str) for x in value):
                raise ValueError('Expected a nonempty string list')
            if len(value) != len(set(value)) or not set(value) <= set(values):
                raise ValueError('Invalid or duplicate labels')
            exclusive = 'Multicolor' if feature == 'colors' else 'Other'
            if exclusive in value and value != [exclusive]:
                raise ValueError('Exclusive value mixed with other labels')
            if feature == 'colors' and len(value) > 2:
                raise ValueError('Too many colors')
        elif not isinstance(value, str) or value not in values:
            raise ValueError('Invalid feature value')
    if set(reasons) != outside or any(not isinstance(v, str) or not v.strip() for v in reasons.values()):
        raise ValueError('Reasons must match outside_schema features exactly')
    merged = {**record['features'], **features}
    if 'strap_style' in merged and 'strap_width' in merged:
        no_straps = merged['strap_style'] in ('Strapless', 'Standard Sleeved')
        if (merged['strap_width'] == 'Not Applicable') != no_straps:
            raise ValueError('Strap dependency conflict: flag for review; never overwrite keywords')
    return merged


def main():
    refs = [json.loads(x) for x in (ROOT / 'poc/feature_extraction/reference/products.jsonl').read_text().splitlines()]
    with (ROOT / 'data/processed/fashiongen/products_train.csv').open(newline='') as f:
        source = {r['product_id']: r for r in csv.DictReader(f)}
    products = {r['product_id']: r for r in map(json.loads, (ROOT / 'extraction/results/products_train.jsonl').open())}
    image_map = {}
    with (ROOT / 'data/processed/fashiongen/images_train.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            image_map.setdefault(row['product_id'], []).append('data/processed/fashiongen/' + row['image_path'])
    with (ROOT / 'poc/feature_extraction/samples/pilot_900/products.csv').open(newline='') as f:
        pilot = list(csv.DictReader(f))
    for category, slug in [('T-shirts', 't-shirts'), ('Dresses', 'dresses'), ('Tank tops & Camisoles', 'tank-tops-and-camisoles')]:
        # Previews only: choose a target with many missing fields; neighbors are
        # illustrative until embeddings exist. No labels from the target leak in.
        targets = [products[r['product_id']] for r in pilot if r['category'] == category
                   and r['product_id'] not in {e['product_id'] for e in refs}]
        target = max(targets, key=lambda r: len(requested_rules(r)))
        examples = []
        for ref in refs:
            if ref['category'] == category and ref['features']['gender'] == target['features']['gender']:
                paths = {x['image_id']: x['path'] for x in ref['images']}
                examples.append({'record': ref, 'source': source[ref['product_id']],
                                 'images': [paths[i] for i in ref['example_image_ids']]})
                if len(examples) == 2:
                    break
        payload = build_prompt(target, source[target['product_id']], image_map[target['product_id']], examples)
        prefix = PROMPTS / 'previews' / slug
        prefix.with_suffix('.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        preview = ['# Prompt preview: ' + category, '',
                   'Offline preview; references are illustrative, not embedding-selected.',
                   f"Target ID: {target['product_id']}. Reference IDs: " + ', '.join(e['record']['product_id'] for e in examples),
                   '', '## System instruction', '', payload['system_instruction'], '## User content', '']
        for part in payload['parts']:
            preview.append(part.get('text') or f"[IMAGE: {part['local_image_path']}]")
            preview.append('')
        preview.extend(['## API generation config (not duplicated in prompt)', '', '```json',
                        json.dumps(payload['generation_config'], indent=2), '```', ''])
        prefix.with_suffix('.md').write_text('\n'.join(preview))
        print(category, target['product_id'], list(requested_rules(target)))


if __name__ == '__main__':
    main()
