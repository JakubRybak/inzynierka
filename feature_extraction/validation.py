"""Validate feature values against shared contracts, regardless of their origin."""
import math

from .schema import allowed_values, is_multi_value, list_constraints


def validate_value(value, definition):
    allowed = allowed_values(definition)
    if is_multi_value(definition):
        if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
            raise ValueError('Expected a nonempty string list')
        if len(value) != len(set(value)) or not set(value) <= allowed:
            raise ValueError('Invalid or duplicate labels')
        exclusive, max_items = list_constraints(definition)
        if any(v in value for v in exclusive) and len(value) != 1:
            raise ValueError('Exclusive value mixed with other labels')
        if len(value) > max_items:
            raise ValueError('Too many feature values')
    elif definition['type'] == 'composition':
        special = definition.get('special_values', [])
        if isinstance(value, str) and value in special:
            return
        if (not isinstance(value, dict) or not value or not set(value) <= allowed - set(special)
                or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in value.values())):
            raise ValueError('Invalid percentage composition')
        if not math.isclose(sum(value.values()), definition['total'], rel_tol=0, abs_tol=definition['tolerance']):
            raise ValueError('Composition total does not match schema')
    elif not isinstance(value, str) or value not in allowed:
        raise ValueError('Invalid feature value')


def validate_features(features, schema, complete=False):
    if not isinstance(features, dict) or set(features) - set(schema):
        raise ValueError('Unknown features')
    if complete and set(features) != set(schema):
        raise ValueError('Incomplete feature set')
    for feature, value in features.items():
        try:
            validate_value(value, schema[feature])
        except ValueError as error:
            raise ValueError(f'{feature}: {error}') from error
    for feature, definition in schema.items():
        dependency = definition.get('value_dependency')
        if dependency and feature in features and dependency['feature'] in features:
            applies = features[dependency['feature']] in dependency['in']
            if (features[feature] == dependency['value']) != applies:
                raise ValueError(f'{feature}: dependency conflict; never overwrite assigned values')


def validate(records, schemas):
    """Validate persisted extraction records, including metadata and exclusions."""
    ids = [record['product_id'] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate product IDs')
    for record in records:
        schema = schemas[(record['section'], record['category'])]
        if not isinstance(record['brand'], str):
            raise ValueError('Invalid brand')
        brand_missing = not record['brand'].strip()
        if brand_missing != any(reason == {'feature': 'brand', 'reason': 'empty'} for reason in record['exclusion_reasons']):
            raise ValueError('Brand exclusion mismatch')
        if set(record['feature_metadata']) != set(schema):
            raise ValueError('Feature metadata must cover the full schema')
        for feature, meta in record['feature_metadata'].items():
            if (feature in record['features']) != (meta['status'] == 'assigned'):
                raise ValueError(f'{feature}: metadata/value mismatch')
        if (record['status'] == 'excluded') != bool(record['exclusion_reasons']):
            raise ValueError('Exclusion status mismatch')
        validate_features(record['features'], schema, complete=record['status'] == 'ready')
