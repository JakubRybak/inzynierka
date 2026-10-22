"""Build product/image manifests and lossless PNG files from Fashion-Gen HDF5."""
import argparse
import csv
import re
import struct
import zlib
from pathlib import Path

import h5py
import numpy as np
import yaml

BASE = Path(__file__).resolve().parents[1]
FIELDS = ['productID', 'name', 'brand', 'gender', 'category', 'subcategory',
          'season', 'msrpUSD', 'composition', 'description', 'pose']


def decode(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace').strip()
    return value.item() if isinstance(value, np.generic) else value


def source_key(value):
    category, _, subcategory = value.partition(' / ')
    return category.strip(), subcategory.strip() or None


def load_taxonomy(path):
    data = yaml.safe_load(path.read_text())
    rules, exclusions, categories = [], [], []
    for section, leaves in data['taxonomy'].items():
        for category, entries in leaves.items():
            categories.append((section, category))
            for entry in entries:
                entry = {'from': entry} if isinstance(entry, str) else entry
                rules.append({
                    'section': section, 'category': category,
                    'source': source_key(entry['from']),
                    'name': re.compile(entry['name'], re.I) if entry.get('name') else None,
                    'desc_not': re.compile(entry['desc_not'], re.I) if entry.get('desc_not') else None,
                })
    for reason, entries in data['excluded'].items():
        for entry in entries:
            if not isinstance(entry, str):
                raise ValueError('Exclusions must be source strings; name exclusions are unsupported.')
            exclusions.append((source_key(entry), reason))
    plain = [r['source'] for r in rules if r['name'] is None]
    if len(set(plain)) != len(plain):
        raise ValueError('Duplicate unconditional category assignments.')
    excluded_keys = [key for key, _ in exclusions]
    if len(set(excluded_keys)) != len(excluded_keys):
        raise ValueError('Duplicate exclusions.')
    for category, subcategory in plain:
        if (category, subcategory) in excluded_keys or (category, None) in excluded_keys:
            raise ValueError(f'Conflicting assignment and exclusion: {category}/{subcategory}')
    rules.sort(key=lambda rule: rule['name'] is None)
    return rules, exclusions, categories


def classify(product, rules, exclusions):
    key = product['category'], product['subcategory']
    for rule in rules:
        if key != rule['source']:
            continue
        if rule['name'] and not rule['name'].search(str(product.get('name', ''))):
            continue
        if rule['desc_not'] and rule['desc_not'].search(str(product.get('description', ''))):
            continue
        return rule['section'], rule['category'], ''
    for (category, subcategory), reason in exclusions:
        if key[0] == category and (subcategory is None or subcategory == key[1]):
            return '', '', reason
    raise ValueError(f'Unmapped source category: {key}')


def write_png(path, array):
    """Encode original uint8 RGB pixels without resizing or a Pillow dependency."""
    if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(f'Expected uint8 RGB image, got {array.shape}/{array.dtype}')
    height, width, _ = array.shape
    def chunk(kind, payload):
        return struct.pack('!I', len(payload)) + kind + payload + struct.pack('!I', zlib.crc32(kind + payload))
    scanlines = b''.join(b'\0' + row.tobytes() for row in array)
    content = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0))
               + chunk(b'IDAT', zlib.compress(scanlines, 3)) + chunk(b'IEND', b''))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def build(inputs, taxonomy, output, export_images=True):
    rules, exclusions, _ = load_taxonomy(taxonomy)
    products, images = [], []
    seen_ids = set()
    for split, source in inputs:
        source = source.resolve()
        with h5py.File(source, 'r') as file:
            required = ['input_productID', 'input_category', 'input_subcategory', 'input_image', 'input_pose']
            for field in required:
                if field not in file:
                    raise ValueError(f'Missing {field} in {source}')
            metadata = {field: file['input_' + field][:].reshape(len(file['input_productID']), -1)[:, 0]
                        for field in FIELDS if 'input_' + field in file}
            groups = {}
            for row, value in enumerate(metadata['productID']):
                groups.setdefault(str(decode(value)), []).append(row)
            for product_id, rows in groups.items():
                if product_id in seen_ids:
                    raise ValueError(f'Product {product_id} occurs in multiple inputs; resolve split overlap first.')
                seen_ids.add(product_id)
                if not re.fullmatch(r'[A-Za-z0-9_-]+', product_id):
                    raise ValueError(f'Unsafe product ID: {product_id}')
                record = {field: decode(values[rows[0]]) for field, values in metadata.items() if field != 'pose'}
                for field, values in metadata.items():
                    if field != 'pose' and any(decode(values[row]) != record[field] for row in rows):
                        raise ValueError(f'Inconsistent {field} for product {product_id}')
                section, category, reason = classify(record, rules, exclusions)
                if reason:
                    continue
                record['original_section'] = record.pop('category')
                record['original_category'] = record.pop('subcategory')
                record.update(product_id=product_id, split=split,
                              section=section, category=category)
                unique_poses = {}
                for row in rows:
                    pose = str(decode(metadata['pose'][row]))
                    if not re.fullmatch(r'[A-Za-z0-9_-]+', pose):
                        raise ValueError(f'Unsafe pose: {pose}')
                    if pose in unique_poses:
                        if not np.array_equal(file['input_image'][row], file['input_image'][unique_poses[pose]]):
                            raise ValueError(f'Different images share product/pose: {product_id}/{pose}')
                        continue
                    unique_poses[pose] = row
                    image_id = f'{product_id}_{pose}'
                    relative = Path('images') / split / product_id / f'{image_id}.png'
                    images.append({'image_id': image_id, 'product_id': product_id, 'split': split,
                                   'source_h5': str(source), 'source_row': row, 'pose': pose,
                                   'image_path': relative.as_posix() if export_images else ''})
                record['image_count'] = len(unique_poses)
                products.append(record)
    # Validate all metadata before producing output or exporting pixels.
    if output.exists() and any(output.iterdir()):
        raise ValueError(f'Output directory must be empty: {output}')
    output.mkdir(parents=True, exist_ok=True)
    if export_images:
        by_source = {}
        for image in images:
            by_source.setdefault(image['source_h5'], []).append(image)
        for source, entries in by_source.items():
            with h5py.File(source, 'r') as file:
                for index, image in enumerate(entries, 1):
                    write_png(output / image['image_path'], file['input_image'][image['source_row']])
                    if index % 5000 == 0:
                        print(f'Exported {index}/{len(entries)} images from {Path(source).name}', flush=True)
    fields = ['product_id', 'section', 'category', 'image_count'] + [
        {'category': 'original_section', 'subcategory': 'original_category'}.get(f, f)
        for f in FIELDS if f not in ('productID', 'pose')]
    for split, _ in inputs:
        write_csv(output / f'products_{split}.csv',
                  [p for p in products if p['split'] == split], fields)
        write_csv(output / f'images_{split}.csv',
                  [image for image in images if image['split'] == split],
                  ['image_id', 'product_id', 'pose', 'image_path'])
    print(f'Saved {len(products)} products and {len(images)} image references to {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train', type=Path)
    parser.add_argument('--validation', type=Path)
    parser.add_argument('--taxonomy', type=Path, default=BASE / 'config/fashiongen_taxonomy.yaml')
    parser.add_argument('--output', type=Path, default=BASE / 'data/processed/fashiongen')
    parser.add_argument('--metadata-only', action='store_true', help='Skip PNG export; image paths remain empty.')
    args = parser.parse_args()
    inputs = [(split, path) for split, path in [('train', args.train), ('validation', args.validation)] if path]
    if not inputs:
        parser.error('Provide --train and/or --validation.')
    build(inputs, args.taxonomy, args.output, not args.metadata_only)


if __name__ == '__main__':
    main()
