"""Execute keyword rules without defining product feature contracts."""
import copy
import re
from pathlib import Path

from ..config_io import read_yaml
from ..schema import allowed_values
from .composition import composition
from .text import normalize, phrase

OPTIONS = {
    'source_value': {'column'},
    'source_map': {'column', 'mapping'},
    'colors': {'columns', 'keywords', 'ignore_column', 'absorb_nested_matches', 'multicolor_value'},
    'composition': {'columns', 'keywords', 'main_sections'},
    'single': {'columns', 'keywords'},
    'single_or_other': {'columns', 'keywords', 'conflict_value'},
    'multi': {'columns', 'keywords'},
    'priority': {'columns', 'keywords'},
}
OPTIONAL = {
    'composition': {'section_only', 'main_section_patterns', 'fallback', 'default_value'},
    'single': {'default_value'},
    'priority': {'default_value'},
}


def validate_rule(name, rule, definition):
    strategy = rule.get('strategy')
    if strategy not in OPTIONS:
        raise ValueError(f'{name}: unknown keyword strategy {strategy}')
    unknown = set(rule) - {'strategy', 'exclude_phrases'} - OPTIONS[strategy] - OPTIONAL.get(strategy, set())
    missing = OPTIONS[strategy] - set(rule)
    if unknown or missing:
        raise ValueError(f'{name}: unknown keys {unknown}, missing keys {missing}')
    allowed = allowed_values(definition)
    if strategy not in {'source_value', 'source_map'}:
        columns, keywords = rule['columns'], rule['keywords']
        if (not isinstance(columns, list) or not columns or any(not isinstance(c, str) or not c.strip() for c in columns)
                or not isinstance(keywords, dict) or not keywords):
            raise ValueError(f'{name}: columns and nonempty keywords required')
        for value, phrases in keywords.items():
            if (value not in allowed or not isinstance(phrases, list) or not phrases
                    or any(not isinstance(k, str) or not k.strip() for k in phrases)):
                raise ValueError(f'{name}: invalid keyword list or unknown value {value}')
    elif not isinstance(rule['column'], str) or not rule['column'].strip():
        raise ValueError(f'{name}: invalid source column')
    if strategy == 'source_map' and (not rule['mapping'] or not set(rule['mapping'].values()) <= allowed):
        raise ValueError(f'{name}: source mapping refers to unknown values')
    expected_type = 'multi_choice' if strategy in {'colors', 'multi'} else 'composition' if strategy == 'composition' else 'single_choice'
    # A composition fallback can return a special scalar such as Unlined.
    if definition['type'] != expected_type and not (definition['type'] == 'composition' and strategy == 'single'):
        raise ValueError(f'{name}: keyword strategy incompatible with schema type')
    for field in ('default_value', 'conflict_value', 'multicolor_value'):
        if field in rule and rule[field] not in allowed:
            raise ValueError(f'{name}: invalid {field}')
    if strategy == 'colors' and rule['multicolor_value'] not in definition.get('exclusive_values', []):
        raise ValueError(f'{name}: multicolor must be exclusive in the schema')
    if 'exclude_phrases' in rule:
        for value, phrases in rule['exclude_phrases'].items():
            if (value not in allowed or not isinstance(phrases, list)
                    or any(not isinstance(k, str) or not k.strip() for k in phrases)):
                raise ValueError(f'{name}: invalid excluded phrases')
    if 'main_section_patterns' in rule:
        patterns = rule['main_section_patterns']
        if (not isinstance(patterns, list) or not patterns
                or any(not isinstance(pattern, str) or not pattern.strip() for pattern in patterns)):
            raise ValueError(f'{name}: expected nonempty section patterns')
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as error:
                raise ValueError(f'{name}: invalid section pattern {pattern}') from error
    if 'fallback' in rule:
        validate_rule(f'{name}.fallback', rule['fallback'], definition)


def load_config(directory, schemas):
    """Load only extraction instructions; missing rules leave schema features unresolved."""
    directory = Path(directory)
    common_path = directory / 'common.yaml'
    common_doc = read_yaml(common_path)
    if set(common_doc) != {'features'}:
        raise ValueError('Invalid common keyword config header')
    common = common_doc['features']
    result, paths = {key: {} for key in schemas}, [common_path]
    seen = set()
    for path in sorted((directory / 'categories').glob('*.yaml')):
        document = read_yaml(path)
        if set(document) != {'section', 'category', 'features'}:
            raise ValueError(f'Invalid category keyword config header: {path}')
        key = document['section'], document['category']
        if key not in schemas or key in seen:
            raise ValueError(f'Unknown or duplicate keyword category: {key}')
        seen.add(key)
        for name, spec in document['features'].items():
            if name not in schemas[key]:
                raise ValueError(f'{key}: unknown keyword feature {name}')
            if 'use' in spec:
                if set(spec) != {'use'} or spec['use'] not in common:
                    raise ValueError(f'{name}: invalid common keyword reference')
                spec = common[spec['use']]
            rule = copy.deepcopy(spec)
            validate_rule(name, rule, schemas[key][name])
            result[key][name] = rule
        paths.append(path)
    return result, paths


def matches(product, rule, keywords=None, columns=None):
    """Return distinct values plus exact match spans for auditing decisions."""
    evidence = {}
    keywords = rule['keywords'] if keywords is None else keywords
    for column in rule['columns'] if columns is None else columns:
        text = normalize(product.get(column, ''))
        if rule.get('ignore_column') and product.get(rule['ignore_column']):
            text = phrase(product[rule['ignore_column']]).sub(' ', text)
        candidates = []
        for value, phrases in keywords.items():
            # Mask excluded phrases only for this value, preserving independent matches.
            value_text = text
            for excluded in rule.get('exclude_phrases', {}).get(value, []):
                value_text = phrase(excluded).sub(lambda m: ' ' * len(m[0]), value_text)
            for keyword in phrases:
                for match in phrase(keyword).finditer(value_text):
                    candidates.append((match.start(), match.end(), value, keyword))
        if rule.get('absorb_nested_matches'):
            candidates = [a for a in candidates if not any(b[0] <= a[0] and b[1] >= a[1] and b[1] - b[0] > a[1] - a[0] for b in candidates)]
        for start, end, value, keyword in candidates:
            item = {'column': column, 'keyword': keyword, 'matched': text[start:end]}
            if item not in evidence.setdefault(value, []):
                evidence[value].append(item)
    return evidence


def resolve_single(hits):
    return next(iter(hits)) if len(hits) == 1 else None



def assign(product, rule, assigned, definition):
    dependency = definition.get('value_dependency')
    if dependency and assigned.get(dependency['feature']) in dependency['in']:
        return dependency['value'], 'assigned', 'derived_rule', {dependency['feature']: assigned[dependency['feature']]}
    if rule is None:
        return None, 'undefined', None, {}
    value, status, source, evidence = assign_rule(product, rule, definition)
    if status in ('undefined', 'no_section') and 'fallback' in rule:
        value, status, source, evidence = assign(product, rule['fallback'], assigned, definition)
    if status != 'assigned' and 'default_value' in rule:
        return rule['default_value'], 'assigned', 'default', evidence
    return value, status, source, evidence


def assign_rule(product, rule, definition):
    strategy = rule['strategy']
    if strategy == 'composition':
        value, status, evidence = composition(product, rule, matches, definition)
        return value, status, 'parser', evidence
    if strategy in {'source_value', 'source_map'}:
        raw = product.get(rule['column'], '').strip()
        value = raw if strategy == 'source_value' and raw in allowed_values(definition) else rule.get('mapping', {}).get(raw)
        return value, 'assigned' if value is not None else 'undefined', 'source_column', {rule['column']: raw}
    hits = matches(product, rule)
    if strategy == 'colors':
        value = [rule['multicolor_value']] if rule['multicolor_value'] in hits or len(hits) > definition['max_items'] else list(hits) or None
    elif strategy in {'single', 'single_or_other'}:
        value = rule['conflict_value'] if strategy == 'single_or_other' and len(hits) >= 2 else resolve_single(hits)
    elif strategy == 'multi':
        exclusive = [v for v in definition.get('exclusive_values', []) if v in hits]
        value = exclusive[:1] if exclusive else list(hits) or None
    elif strategy == 'priority':
        value = next((v for v in rule['keywords'] if v in hits), None)
    else:
        raise ValueError(f'Unimplemented keyword strategy: {strategy}')
    return value, 'assigned' if value is not None else 'undefined', 'keyword', hits


def extract_product(product, rules, schema):
    features, metadata, reasons = {}, {}, []
    brand = product.get('brand') or ''
    if not brand.strip():
        reasons.append({'feature': 'brand', 'reason': 'empty'})
    for feature, definition in schema.items():
        rule = rules.get(feature)
        value, status, source, evidence = assign(product, rule, features, definition)
        metadata[feature] = {'status': status, 'source': source if status == 'assigned' else None,
                             'strategy': rule['strategy'] if rule else None, 'evidence': evidence}
        if status == 'assigned':
            features[feature] = value
        elif definition.get('on_unresolved', 'llm') == 'exclude':
            reasons.append({'feature': feature, 'reason': status})
    return {'product_id': product['product_id'], 'brand': brand,
            'section': product['section'], 'category': product['category'],
            'features': features, 'feature_metadata': metadata,
            'status': 'excluded' if reasons else 'ready' if len(features) == len(schema) else 'pending',
            'exclusion_reasons': reasons}
