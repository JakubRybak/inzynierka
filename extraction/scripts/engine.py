"""Execute keyword rules for Tops, Dresses and Skirts from YAML configuration."""
import copy
import math
import re
from collections import Counter
from pathlib import Path

import yaml

STRATEGIES = {'source_value', 'source_map', 'colors', 'composition', 'single', 'single_or_other', 'multi', 'llm'}
BASE_KEYS = {'strategy', 'columns', 'keywords', 'on_unresolved', 'derive', 'exclude_phrases'}
OPTIONS = {
    'llm': {'allowed_values'},
    'source_value': {'column', 'allowed_values'},
    'source_map': {'column', 'mapping'},
    'colors': {'ignore_column', 'absorb_nested_matches', 'multicolor_value', 'max_named_colors'},
    'composition': {'main_sections', 'total', 'tolerance'},
    'single': set(),
    'single_or_other': {'conflict_value'},
    'multi': {'exclusive_values'},
}
REQUIRED = OPTIONS



def normalize(text):
    return re.sub(r'[\s\-–—]+', ' ', text.casefold()).strip()


def phrase(pattern):
    return re.compile(r'(?<!\w)' + re.escape(normalize(pattern)).replace(r'\ ', r'\s+') + r'(?!\w)')


def read_yaml(path):
    # safe_load rejects arbitrary Python objects; reject duplicate keys as well.
    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError(f'Duplicate YAML key in {path}: {key}')
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    return yaml.load(Path(path).read_text(), Loader=UniqueLoader)


def allowed_values(rule):
    if rule['strategy'] in {'source_value', 'llm'}:
        return set(rule['allowed_values'])
    if rule['strategy'] == 'source_map':
        return set(rule['mapping'].values())
    return set(rule['keywords'])


def validate_rule(name, rule, previous):
    strategy = rule.get('strategy')
    if strategy not in STRATEGIES:
        raise ValueError(f'{name}: unknown strategy {strategy}')
    unknown = set(rule) - BASE_KEYS - OPTIONS[strategy]
    missing = REQUIRED[strategy] - set(rule)
    if unknown or missing:
        raise ValueError(f'{name}: unknown keys {unknown}, missing keys {missing}')
    if rule.get('on_unresolved', 'llm') not in {'llm', 'exclude'}:
        raise ValueError(f'{name}: invalid unresolved action')
    if strategy not in {'source_value', 'source_map', 'llm'}:
        if not rule.get('columns') or not rule.get('keywords'):
            raise ValueError(f'{name}: columns and keywords required')
        for value, keywords in rule['keywords'].items():
            if not isinstance(value, str) or not isinstance(keywords, list) or any(not isinstance(k, str) or not k.strip() for k in keywords):
                raise ValueError(f'{name}: invalid keyword list')
    if strategy == 'llm' and (not rule['allowed_values'] or
                            any(not isinstance(v, str) or not v.strip() for v in rule['allowed_values'])):
        raise ValueError(f'{name}: allowed_values must contain nonempty strings')
    allowed = allowed_values(rule)
    for field in ['exclusive_values']:
        if field in rule and (len(set(rule[field])) != len(rule[field]) or not set(rule[field]) <= allowed):
            raise ValueError(f'{name}: invalid {field}')
    for field in ['conflict_value', 'multicolor_value']:
        if field in rule and rule[field] not in allowed:
            raise ValueError(f'{name}: invalid {field}')
    for field in ['exclude_phrases']:
        if field in rule and not set(rule[field]) <= allowed:
            raise ValueError(f'{name}: {field} refers to unknown values')
    if 'derive' in rule:
        derive = rule['derive']
        if set(derive) != {'feature', 'in', 'value'} or derive['feature'] not in previous or derive['value'] not in allowed:
            raise ValueError(f'{name}: invalid or forward derivation')
        if not set(derive['in']) <= allowed_values(previous[derive['feature']]):
            raise ValueError(f'{name}: invalid derivation trigger')


def load_config(directory):
    directory = Path(directory)
    common_path = directory / 'common.yaml'
    common_doc = read_yaml(common_path)
    if set(common_doc) != {'features'}:
        raise ValueError('Invalid common config header')
    common = common_doc['features']
    result, paths = {}, [common_path]
    for path in sorted((directory / 'categories').glob('*.yaml')):
        document = read_yaml(path)
        if set(document) != {'section', 'category', 'features'}:
            raise ValueError(f'Invalid category config header: {path}')
        key = (document['section'], document['category'])
        if key in result:
            raise ValueError(f'Duplicate category: {key}')
        rules = {}
        for name, spec in document['features'].items():
            if 'use' in spec:
                if set(spec) != {'use'} or spec['use'] not in common:
                    raise ValueError(f'{name}: invalid common reference')
                spec = common[spec['use']]
            rule = copy.deepcopy(spec)
            validate_rule(name, rule, rules)
            rules[name] = rule
        result[key] = rules
        paths.append(path)
    if not result:
        raise ValueError('No configured categories')
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


def composition(product, rule):
    text = product.get(rule['columns'][0], '')
    if not text.strip():
        return None, 'undefined', {}
    # Section boundaries accept Unicode letters and replacement characters from
    # damaged labels. Only exact Main/Body labels can still select the main part.
    chunks = re.split(r'((?:[^\W\d_]|\uFFFD)(?:[^\W_]|[\uFFFD\u0300-\u036f \t/-])*):', text)
    if len(chunks) > 1:
        sections = [(normalize(chunks[i]), chunks[i + 1]) for i in range(1, len(chunks), 2)]
        main = [body for label, body in sections if label in rule['main_sections']]
        if len(main) != 1 or chunks[0].strip(' .;,\n'):
            return None, 'ambiguous_main_section', {}
        text = main[0]
    ingredient = re.compile(r'(\d+(?:\.\d+)?)\s*%\s*([A-Za-z][A-Za-z /-]*)(?=\s*(?:[,;.]|$))')
    ingredients = list(ingredient.finditer(text))
    if not ingredients or ingredient.sub('', text).strip(' ,;.\n\t'):
        return None, 'unparsed_composition', {}
    totals, evidence = Counter(), {}
    for match in ingredients:
        raw_material = match[2].strip()
        hits = matches({rule['columns'][0]: raw_material}, rule)
        material = resolve_single(hits)
        if material is None:
            return None, 'unmapped_material', {'unmapped_material': raw_material}
        totals[material] += float(match[1])
        evidence.setdefault(material, []).append({'material': raw_material, 'percent': float(match[1])})
    if not math.isclose(sum(totals.values()), rule['total'], rel_tol=0, abs_tol=rule['tolerance']):
        return None, 'sum_not_100', {'parsed_total': sum(totals.values())}
    return dict(totals), 'assigned', evidence


def assign(product, rule, assigned):
    strategy = rule['strategy']
    if strategy == 'llm':
        return None, 'undefined', None, {}
    if 'derive' in rule:
        dependency = rule['derive']
        if assigned.get(dependency['feature']) in dependency['in']:
            return dependency['value'], 'assigned', 'derived_rule', {dependency['feature']: assigned[dependency['feature']]}
    if strategy == 'composition':
        value, status, evidence = composition(product, rule)
        return value, status, 'parser', evidence
    if strategy in {'source_value', 'source_map'}:
        raw = product.get(rule['column'], '').strip()
        value = raw if strategy == 'source_value' and raw in rule['allowed_values'] else rule.get('mapping', {}).get(raw)
        return value, 'assigned' if value is not None else 'undefined', 'source_column', {rule['column']: raw}
    hits = matches(product, rule)
    if strategy == 'colors':
        value = [rule['multicolor_value']] if rule['multicolor_value'] in hits or len(hits) > rule['max_named_colors'] else list(hits) or None
    elif strategy in {'single', 'single_or_other'}:
        value = rule['conflict_value'] if strategy == 'single_or_other' and len(hits) >= 2 else resolve_single(hits)
    elif strategy == 'multi':
        exclusive = [v for v in rule['exclusive_values'] if v in hits]
        value = exclusive[:1] if exclusive else list(hits) or None
    else:
        raise ValueError(f'Unimplemented strategy: {strategy}')
    return value, 'assigned' if value is not None else 'undefined', 'keyword', hits



def extract_product(product, rules):
    features, metadata, reasons = {}, {}, []
    brand = product.get('brand') or ''
    if not brand.strip():
        reasons.append({'feature': 'brand', 'reason': 'empty'})
    for feature, rule in rules.items():
        value, status, source, evidence = assign(product, rule, features)
        metadata[feature] = {'status': status, 'source': source if status == 'assigned' else None,
                             'strategy': rule['strategy'], 'evidence': evidence}
        if status == 'assigned':
            features[feature] = value
        elif rule.get('on_unresolved', 'llm') == 'exclude':
            reasons.append({'feature': feature, 'reason': status})
    return {'product_id': product['product_id'], 'brand': brand,
            'section': product['section'], 'category': product['category'],
            'features': features, 'feature_metadata': metadata,
            'status': 'excluded' if reasons else 'ready' if len(features) == len(rules) else 'pending',
            'exclusion_reasons': reasons}
