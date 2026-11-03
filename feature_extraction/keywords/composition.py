"""Parse main composition using the configured material vocabulary."""
import math
import re
from collections import Counter

from .text import normalize

def composition(product, rule, match_material):
    text = product.get(rule['columns'][0], '')
    if not text.strip():
        return None, 'undefined', {}
    # Section boundaries accept Unicode letters and replacement characters from
    # damaged labels. Only exact labels from main_sections can select the main part.
    chunks = re.split(r'((?:[^\W\d_]|\uFFFD)(?:[^\W_]|[\uFFFD\u0300-\u036f \t/-])*):', text)
    if len(chunks) > 1:
        sections = [(normalize(chunks[i]), chunks[i + 1]) for i in range(1, len(chunks), 2)]
        main = [body for label, body in sections if label in rule['main_sections']]
        if rule.get('section_only') and not main:
            return None, 'no_section', {}
        if len(main) != 1 or chunks[0].strip(' .;,\n') and not rule.get('section_only'):
            return None, 'ambiguous_main_section', {}
        text = main[0]
    elif rule.get('section_only'):
        return None, 'no_section', {}
    ingredient = re.compile(r'(\d+(?:\.\d+)?)\s*%\s*([A-Za-z][A-Za-z /-]*)(?=\s*(?:[,;.]|$))')
    ingredients = list(ingredient.finditer(text))
    if not ingredients or ingredient.sub('', text).strip(' ,;.\n\t'):
        return None, 'unparsed_composition', {}
    totals, evidence = Counter(), {}
    for match in ingredients:
        raw_material = match[2].strip()
        hits = match_material({rule['columns'][0]: raw_material}, rule)
        material = next(iter(hits)) if len(hits) == 1 else None
        if material is None:
            return None, 'unmapped_material', {'unmapped_material': raw_material}
        totals[material] += float(match[1])
        evidence.setdefault(material, []).append({'material': raw_material, 'percent': float(match[1])})
    if not math.isclose(sum(totals.values()), rule['total'], rel_tol=0, abs_tol=rule['tolerance']):
        return None, 'sum_not_100', {'parsed_total': sum(totals.values())}
    return dict(totals), 'assigned', evidence
