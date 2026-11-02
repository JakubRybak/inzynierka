"""Build only the requested feature blocks and their response schema."""
import json
from pathlib import Path

from ..keywords.engine import allowed_values, load_config

ROOT = Path(__file__).resolve().parents[2]

PROMPTS = Path(__file__).resolve().parent / 'prompts'
DEFINITIONS = json.loads((PROMPTS / 'feature_definitions.json').read_text())
CONFIGS, _ = load_config(ROOT / 'feature_extraction/keywords/definitions')


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
    if missing:
        definitions = category_definitions(record['category'])
        if set(missing) - set(definitions):
            raise ValueError(f"Unsupported LLM features for {record['category']}: {set(missing) - set(definitions)}")
    return missing


def category_definitions(category):
    if category not in DEFINITIONS:
        raise ValueError(f'No LLM feature definitions for category: {category}')
    return DEFINITIONS[category]


def choices(category, feature, rule):
    allowed = allowed_values(rule)
    definition = category_definitions(category)[feature]
    values = [v for v in definition['values'] if v in allowed]
    if set(values) != allowed:
        raise ValueError(f'Definition/taxonomy mismatch: {category}.{feature}')
    return values


def build_schema(rules, category):
    fields, reasons = {}, {}
    for feature, rule in rules.items():
        values = choices(category, feature, rule)
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
    category = record['category']
    definitions = category_definitions(category)
    definition_lines = ['REQUESTED FEATURES']
    for feature, rule in rules.items():
        definition_lines.extend(['', feature, definitions[feature]['instruction']])
        for value in choices(category, feature, rule):
            definition_lines.append(f"- {value}: {definitions[feature]['values'][value]}")
        definition_lines.append('Other is available: only the listed values are allowed.'
                                if 'Other' in choices(category, feature, rule)
                                else 'Other is unavailable: outside_schema is permitted under the decision rules.')
    # Show this relation only when BOTH features are requested. Otherwise validate
    # it locally after merging, without disclosing a locked value or its definition.
    if 'strap_style' in rules and 'strap_width' in rules:
        styles = ['Strapless']
        if 'Standard Sleeved' in choices(category, 'strap_style', rules['strap_style']):
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
            'responseMimeType': 'application/json', 'responseSchema': build_schema(rules, category),
        },
    }
