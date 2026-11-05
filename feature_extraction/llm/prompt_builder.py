"""Build only the requested feature blocks and their response schema."""
import json
from pathlib import Path

from ..schema import allowed_values, is_multi_value, list_constraints, load_schemas

PROMPTS = Path(__file__).resolve().parent / 'prompts'


def load_definitions(folder):
    common = json.loads((folder / 'common.json').read_text())
    categories = {}
    for path in sorted((folder / 'categories').glob('*.json')):
        document = json.loads(path.read_text())
        if set(document) != {'category', 'features'}:
            raise ValueError(f'Invalid category prompt file: {path}')
        category = document['category']
        if category in categories:
            raise ValueError(f'Duplicate category prompt definitions: {category}')
        categories[category] = document['features']
    return common, categories


COMMON_DEFINITIONS, DEFINITIONS = load_definitions(PROMPTS)
SCHEMAS, _ = load_schemas()


def obj(properties, required=None):
    return {'type': 'OBJECT', 'properties': properties,
            'required': list(properties) if required is None else required,
            'propertyOrdering': list(properties)}


def enum(values):
    return {'type': 'STRING', 'enum': values}


def requested_features(record):
    rules = SCHEMAS[(record['section'], record['category'])]
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
    return {**COMMON_DEFINITIONS, **DEFINITIONS[category]}


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
        if is_multi_value(rule):
            _, max_items = list_constraints(rule)
            value_schema = {'type': 'ARRAY', 'items': enum(values), 'minItems': 1,
                            'maxItems': max_items}
            if not has_other:
                value_schema = {'anyOf': [value_schema, enum(['outside_schema'])]}
        elif rule['type'] == 'composition':
            specials = rule.get('special_values', [])
            materials = {value: {'type': 'NUMBER', 'minimum': 0, 'maximum': rule['total']}
                         for value in values if value not in specials}
            variants = [obj(materials, required=[])]
            if specials:
                variants.append(enum(specials))
            if not has_other:
                variants.append(enum(['outside_schema']))
            value_schema = {'anyOf': variants}
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
    rules = requested_features(record)
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
    # Include a dependency only when both features are requested; assigned values stay hidden.
    for feature, definition in rules.items():
        dependency = definition.get('value_dependency')
        if dependency and dependency['feature'] in rules:
            definition_lines.extend(['', 'JOINT CONSTRAINT',
                feature + ' must equal ' + dependency['value'] + ' if and only if '
                + dependency['feature'] + ' is ' + ' or '.join(dependency['in']) + '.'])
    parts = [{'text': '\n'.join(definition_lines)}, {'text':
        'The following two reference products illustrate the requested labels. '
        'They are not the target. Their labels are examples, not predictions for the target.'}]
    for i, example in enumerate(examples, 1):
        ref = example['record']; raw = example['source']
        payload = {'name': raw['name'], 'description': raw['description']}
        if 'insulation' in rules:
            payload['composition'] = raw['composition']
        payload['labels'] = {key: ref['features'][key] for key in rules}
        parts.append({'text': f'REFERENCE {i}\n' + json.dumps(payload, ensure_ascii=False)})
        for img in example['images']:
            parts.extend([{'text': f'REFERENCE {i} IMAGE'}, {'local_image_path': img}])
    target = {'category': record['category'], 'name': source['name'], 'description': source['description']}
    if 'insulation' in rules:
        target['composition'] = source['composition']
    parts.append({'text': 'TARGET PRODUCT\n' + json.dumps(target, ensure_ascii=False)})
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
