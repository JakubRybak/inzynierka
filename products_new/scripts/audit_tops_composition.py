"""Audit raw compositions for taxonomy Tops; no images or source data modified."""
import csv
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import h5py

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports'
SUBS = {'T-SHIRTS', 'POLOS', 'TANK TOPS', 'TANK TOPS & CAMISOLES', 'BODYSUITS'}
PERCENT = re.compile(r'(\d+(?:[.,]\d+)?)\s*%')

def total(s):
    vals = PERCENT.findall(s)
    return str(sum((Decimal(v.replace(',', '.')) for v in vals), Decimal(0))) if vals else None

products = {}
variants = defaultdict(set)
split_ids = defaultdict(set)
for split in ('train', 'validation'):
    with h5py.File(BASE / 'data/raw' / f'fashiongen_256_256_{split}.h5') as f:
        cols = {k: f[k][:].reshape(-1) for k in ('input_productID', 'input_category', 'input_subcategory', 'input_composition', 'input_name')}
    for pid, cat, sub, raw, name in zip(*cols.values()):
        if cat != b'TOPS' or sub.decode(errors='replace') not in SUBS:
            continue
        pid = int(pid)
        text = raw.decode('utf-8', errors='replace')
        split_ids[split].add(pid)
        variants[pid].add(text)
        products.setdefault(pid, dict(product_id=pid, split=split, subcategory=sub.decode(), name=name.decode(errors='replace'), composition=text))

counts = Counter()
by_sub = defaultdict(Counter)
examples = defaultdict(list)
rows = []
for pid, item in products.items():
    s = item['composition']
    ncolon = s.count(':')
    sm = total(s)
    if ncolon:
        status = 'named_sections_present'
    elif sm is None:
        status = 'no_colon_no_percentages'
    elif Decimal(sm) == 100:
        status = 'no_colon_sum_100'
    else:
        status = 'no_colon_sum_not_100'
    counts[status] += 1
    by_sub[item['subcategory']][status] += 1
    if len(examples[status]) < 12:
        examples[status].append(item)
    rows.append(dict(**item, colon_count=ncolon, all_percentages_sum=sm, status=status))

summary = dict(
    scope='TOPS category with subcategories T-SHIRTS, POLOS, TANK TOPS, TANK TOPS & CAMISOLES, BODYSUITS; unique input_productID across train and validation',
    unique_products=len(products), products_per_split={k:len(v) for k,v in split_ids.items()},
    inconsistent_compositions_per_product=sum(len(v)>1 for v in variants.values()),
    counts=dict(counts), by_subcategory={k:dict(v) for k,v in by_sub.items()},
    colon_count_distribution=dict(Counter(r['colon_count'] for r in rows)),
    examples=dict(examples),
    interpretation='Sums are literal sums of every percentage in raw text, not a validated main-body composition. Colon-free sum=100 alone does not guarantee semantic completeness. Named sections require separate interpretation; percentages of different garment parts must not be added as a whole-garment composition.'
)
OUT.mkdir(exist_ok=True)
(OUT/'tops_composition_audit.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
with (OUT/'tops_composition_audit.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(json.dumps({k:v for k,v in summary.items() if k!='examples'}, ensure_ascii=False, indent=2))
print('\nEXCEPTIONS WITHOUT NAMED SECTIONS:')
for r in rows:
    if r['status'] in ('no_colon_sum_not_100','no_colon_no_percentages'):
        print(r['product_id'],r['subcategory'],repr(r['composition']),r['all_percentages_sum'])
print('\nNAMED-SECTION EXAMPLES:')
for r in examples['named_sections_present'][:8]:
    print(r['product_id'],repr(r['composition']))
