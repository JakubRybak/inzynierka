"""Extract keyword features for every product in the configured categories."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

import pyarrow as pa
import pyarrow.parquet as pq
from engine import extract_product, load_config, allowed_values

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parents[1]
JSON_COLUMNS = ['features', 'feature_metadata', 'exclusion_reasons']
COLUMNS = ['product_id', 'brand', 'section', 'category', *JSON_COLUMNS[:2], 'status', JSON_COLUMNS[2]]


def validate(records, configs):
    assert len({r['product_id'] for r in records}) == len(records)
    for record in records:
        assert isinstance(record['brand'], str)
        brand_missing = not record['brand'].strip()
        assert brand_missing == any(reason == {'feature': 'brand', 'reason': 'empty'}
                                    for reason in record['exclusion_reasons'])
        rules = configs[(record['section'], record['category'])]
        assert set(record['feature_metadata']) == set(rules)
        for feature, meta in record['feature_metadata'].items():
            assert (feature in record['features']) == (meta['status'] == 'assigned')
            if feature in record['features']:
                value = record['features'][feature]
                assert value is not None and value != []
                values = set(value) if isinstance(value, (list, dict)) else {value}
                assert values <= allowed_values(rules[feature]), (feature, value)
        assert (record['status'] == 'excluded') == bool(record['exclusion_reasons'])
        assert record['status'] != 'ready' or len(record['features']) == len(rules)
        if 'colors' in record['features']:
            colors = record['features']['colors']
            rule = rules['colors']
            assert len(colors) <= rule['max_named_colors']
            assert rule['multicolor_value'] not in colors or colors == [rule['multicolor_value']]
        if 'main_composition' in record['features']:
            rule = rules['main_composition']
            assert abs(sum(record['features']['main_composition'].values()) - rule['total']) <= rule['tolerance']
        for feature, rule in rules.items():
            if 'derive' in rule and record['features'].get(rule['derive']['feature']) in rule['derive']['in']:
                assert record['features'][feature] == rule['derive']['value']


def write_output(directory, split, records):
    rows = [{key: json.dumps(value, ensure_ascii=False, sort_keys=True) if key in JSON_COLUMNS else value
             for key, value in row.items()} for row in records]
    table = pa.Table.from_pylist(rows, schema=pa.schema([(key, pa.string()) for key in COLUMNS]))
    path = directory / f'products_{split}.parquet'
    pq.write_table(table, path, compression='zstd')
    restored = pq.read_table(path).to_pylist()
    for row in restored:
        for column in JSON_COLUMNS:
            row[column] = json.loads(row[column])
    assert restored == records, 'Parquet read-back mismatch'
    (directory / f'products_{split}.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=BASE / 'config')
    parser.add_argument('--dataset', type=Path, default=ROOT / 'data/processed/fashiongen')
    parser.add_argument('--output', type=Path, default=BASE / 'results')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing extraction outputs.')
    args = parser.parse_args()
    configs, _ = load_config(args.config)
    if args.output.resolve() == args.dataset.resolve() or args.dataset.resolve() in args.output.resolve().parents:
        parser.error('Output must be separate from the input dataset directory.')
    splits = ['train', 'validation']
    filenames = [f'products_{split}.{extension}' for split in splits for extension in ['parquet', 'jsonl']]
    if not args.overwrite and any((args.output / name).exists() for name in filenames):
        parser.error('Extraction outputs already exist. Use --overwrite to replace them.')
    args.output.mkdir(parents=True, exist_ok=True)
    all_ids, total_statuses = set(), Counter()
    total_products = 0
    # Validate both splits before publishing any output. Temporary files are removed on failure.
    with TemporaryDirectory(prefix='.extraction-', dir=args.output) as temporary:
        staging = Path(temporary)
        for split in splits:
            print(f'Processing {split}...', flush=True)
            records, selected_categories, skipped_categories = [], Counter(), Counter()
            with (args.dataset / f'products_{split}.csv').open(newline='', encoding='utf-8') as file:
                for product in csv.DictReader(file):
                    key = (product['section'], product['category'])
                    if key not in configs:
                        skipped_categories[' / '.join(key)] += 1
                        continue
                    records.append(extract_product(product, configs[key]))
                    selected_categories[key] += 1
            missing = set(configs) - set(selected_categories)
            if missing:
                raise ValueError(f'Configured categories absent from {split}: {sorted(missing)}')
            records.sort(key=lambda r: (r['section'], r['category'], r['product_id']))
            validate(records, configs)
            assert not all_ids.intersection(r['product_id'] for r in records), 'Train/validation ID overlap'
            all_ids.update(r['product_id'] for r in records)
            write_output(staging, split, records)
            statuses = Counter(r['status'] for r in records)
            total_statuses.update(statuses)
            total_products += len(records)
            print(json.dumps({'split': split, 'products': len(records), 'statuses': dict(statuses),
                              'categories': {category: count for (_, category), count in selected_categories.items()},
                              'skipped_categories': dict(skipped_categories)}, ensure_ascii=False, indent=2), flush=True)
        for name in filenames:
            (staging / name).replace(args.output / name)
    print(json.dumps({'products': total_products, 'statuses': dict(total_statuses),
                      'output': str(args.output)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
