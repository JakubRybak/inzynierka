"""Validate model output and enforce cross-feature constraints."""
from .prompt_builder import requested_rules, choices

def validate_response(response, record):
    """Business validation beyond server schema; does not mutate keyword values."""
    rules = requested_rules(record)
    category = record['category']
    reason_field = any('Other' not in choices(category, f, rule) for f, rule in rules.items())
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
        values = choices(category, feature, rules[feature])
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


def merge_result(original, response, metadata):
    import copy
    merged = validate_response(response, original)
    record = copy.deepcopy(original)
    record.update(product_status=response['product_status'], product_reason=response['product_reason'],
                  outside_schema_reasons=response.get('outside_schema_reasons', {}), llm_metadata=metadata,
                  annotation_origin='llm')
    if merged is None:
        record['status'] = 'needs_review'
        return record
    for feature, value in response['features'].items():
        unresolved = value == 'outside_schema'
        record['feature_metadata'][feature] = {
            'status': 'outside_schema' if unresolved else 'assigned', 'source': 'llm',
            'strategy': 'structured_output',
            'evidence': {'call_id': metadata['call_id'],
                         **({'reason': response['outside_schema_reasons'][feature]} if unresolved else {})}}
        if not unresolved:
            record['features'][feature] = value
    record['status'] = 'pending' if response.get('outside_schema_reasons') else 'ready'
    if any(record['features'].get(k) != v for k, v in original['features'].items()):
        raise ValueError('Keyword assignment changed')
    return record
