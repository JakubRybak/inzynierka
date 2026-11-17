"""Load category contracts and validate their values and constraints."""
import copy
import math
from pathlib import Path

from ..config_io import read_yaml

DIRECTORY = Path(__file__).resolve().parent
TYPES = {'single_choice', 'multi_choice', 'composition'}


def allowed_values(definition):
    return set(definition['values'])


def is_multi_value(definition):
    return definition['type'] == 'multi_choice'


def list_constraints(definition):
    return definition.get('exclusive_values', []), definition['max_items']


def validate_definition(name, definition, previous):
    kind = definition.get('type')
    if kind not in TYPES:
        raise ValueError(f'{name}: invalid feature type {kind}')
    fields = {'type', 'values', 'value_dependency', 'on_unresolved'}
    if kind == 'multi_choice':
        fields |= {'max_items', 'exclusive_values'}
    if kind == 'composition':
        fields |= {'total', 'tolerance', 'special_values'}
    if set(definition) - fields:
        raise ValueError(f'{name}: unknown schema keys {set(definition) - fields}')
    values = definition.get('values')
    if (not isinstance(values, list) or not values
            or any(not isinstance(v, str) or not v.strip() for v in values)
            or len(values) != len(set(values))):
        raise ValueError(f'{name}: expected distinct nonempty values')
    if definition.get('on_unresolved', 'llm') not in ('llm', 'exclude'):
        raise ValueError(f'{name}: invalid unresolved action')
    for field in ('exclusive_values', 'special_values'):
        selected = definition.get(field, [])
        if (not isinstance(selected, list) or any(not isinstance(v, str) for v in selected)
                or len(selected) != len(set(selected)) or not set(selected) <= set(values)):
            raise ValueError(f'{name}: invalid {field}')
    if kind == 'multi_choice':
        limit = definition.get('max_items')
        if type(limit) is not int or not 1 <= limit <= len(values):
            raise ValueError(f'{name}: invalid max_items')
    if kind == 'composition':
        for field in ('total', 'tolerance'):
            value = definition.get(field)
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name}: {field} must be positive and finite')
        if set(definition.get('special_values', [])) == set(values):
            raise ValueError(f'{name}: composition needs material values')
    if 'value_dependency' in definition:
        dependency = definition['value_dependency']
        if (not isinstance(dependency, dict) or set(dependency) != {'feature', 'in', 'value'}
                or dependency['feature'] not in previous or dependency['value'] not in values):
            raise ValueError(f'{name}: invalid or forward value dependency')
        triggers = dependency['in']
        if (not isinstance(triggers, list) or not triggers or any(not isinstance(v, str) for v in triggers)
                or len(triggers) != len(set(triggers))
                or not set(triggers) <= allowed_values(previous[dependency['feature']])):
            raise ValueError(f'{name}: invalid dependency triggers')
        if previous[dependency['feature']]['type'] != 'single_choice' or kind != 'single_choice':
            raise ValueError(f'{name}: value dependency requires single-choice features')


def load_schemas(directory=DIRECTORY):
    directory = Path(directory)
    common_path = directory / 'common.yaml'
    common = read_yaml(common_path)
    if not isinstance(common, dict) or set(common) != {'features'}:
        raise ValueError('Invalid common schema header')
    result, paths = {}, [common_path]
    for path in sorted((directory / 'categories').glob('*.yaml')):
        document = read_yaml(path)
        if set(document) != {'section', 'category', 'features'}:
            raise ValueError(f'Invalid category schema header: {path}')
        key = document['section'], document['category']
        if key in result:
            raise ValueError(f'Duplicate category schema: {key}')
        features = {}
        for name, spec in document['features'].items():
            if 'use' in spec:
                if set(spec) != {'use'} or spec['use'] not in common['features']:
                    raise ValueError(f'{name}: invalid common schema reference')
                spec = common['features'][spec['use']]
            definition = copy.deepcopy(spec)
            validate_definition(name, definition, features)
            features[name] = definition
        if not features:
            raise ValueError(f'Empty category schema: {key}')
        result[key] = features
        paths.append(path)
    if not result:
        raise ValueError('No configured category schemas')
    return result, paths
