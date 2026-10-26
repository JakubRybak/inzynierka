"""Local data, image selection and nearest-reference retrieval for the PoC."""
import copy
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from build_prompt import ROOT, CONFIGS, requested_rules, build_prompt, validate_response

CATEGORIES = ['T-shirts', 'Dresses', 'Tank tops & Camisoles']


def example_images(images):
    """Always select source poses 1 and 3, without claiming a semantic view."""
    by_pose = {r['pose']: r for r in images}
    return [by_pose[pose] for pose in ('id_gridfs_1', 'id_gridfs_3')]


class Dataset:
    def __init__(self):
        with (ROOT / 'poc/feature_extraction/samples/pilot_900/products.csv').open(newline='') as f:
            self.pilot = list(csv.DictReader(f))
        self.ids = {r['product_id'] for r in self.pilot}
        with (ROOT / 'data/processed/fashiongen/products_train.csv').open(newline='') as f:
            self.source = {r['product_id']: r for r in csv.DictReader(f) if r['product_id'] in self.ids}
        with (ROOT / 'extraction/results/products_train.jsonl').open() as stream:
            self.keywords = {r['product_id']: r for r in map(json.loads, stream) if r['product_id'] in self.ids}
        self.images = {}
        with (ROOT / 'data/processed/fashiongen/images_train.csv').open(newline='') as f:
            for row in csv.DictReader(f):
                if row['product_id'] in self.ids:
                    self.images.setdefault(row['product_id'], []).append({
                        **row, 'path': 'data/processed/fashiongen/' + row['image_path']})
        with (ROOT / 'poc/feature_extraction/reference/products.jsonl').open() as stream:
            self.bank = {r['product_id']: r for r in map(json.loads, stream)}
        self.initial_reference_ids = set(self.bank)
        folder = ROOT / 'poc/feature_extraction/embeddings/gemini_embedding_2'
        manifest = json.loads((folder / 'manifest.json').read_text())
        if not manifest['complete']:
            raise ValueError('Incomplete embedding run')
        self.vectors = {}
        self.embedding_manifest = manifest
        for modality in ('image', 'text'):
            rows = pq.read_table(folder / (modality + '.parquet')).to_pylist()
            if len(rows) != len(self.ids) or {r['product_id'] for r in rows} != self.ids:
                raise ValueError('Embedding IDs differ from pilot')
            self.vectors[modality] = {r['product_id']: np.asarray(r['embedding'], dtype=np.float32) for r in rows}
            for row in rows:
                pid = row['product_id']
                content = ((ROOT / self.images[pid][0]['path']).read_bytes() if modality == 'image'
                           else self.source[pid]['description'].encode('utf-8'))
                if hashlib.sha256(content).hexdigest() != row['input_sha256']:
                    raise ValueError(f'Stale {modality} embedding for {pid}')
                v = self.vectors[modality][pid]
                if not np.isfinite(v).all() or not np.isclose(np.linalg.norm(v), 1, atol=1e-5):
                    raise ValueError('Invalid normalized embedding')
        for r in self.bank.values():
            self.check_reference(r)

    def check_reference(self, record):
        pid = record['product_id']
        rules = CONFIGS[(record['section'], record['category'])]
        if pid not in self.ids or record['status'] != 'ready' or set(record['features']) != set(rules):
            raise ValueError('Reference must have all features and be ready')
        if record.get('product_status', 'ok') != 'ok':
            raise ValueError('Reference has a product-level problem')
        if any(v == 'outside_schema' for v in record['features'].values()):
            raise ValueError('Reference contains unresolved feature')
        example_images(self.images[pid])

    def select_targets(self, per_category):
        selected = []
        for category in CATEGORIES:
            candidates = [self.keywords[r['product_id']] for r in self.pilot
                          if r['category'] == category and r['product_id'] not in self.initial_reference_ids
                          and self.keywords[r['product_id']]['status'] != 'excluded']
            if len(candidates) < per_category:
                raise ValueError('Not enough targets')
            # First product for the ordinary path; then an opposite-gender product
            # with many missing features when that gender exists.
            first = candidates[0]; chosen = [first]
            if per_category > 1:
                opposite = [r for r in candidates if r['features']['gender'] != first['features']['gender']]
                pool = opposite or [r for r in candidates if r['product_id'] != first['product_id']]
                chosen.append(max(pool, key=lambda r: len(requested_rules(r))))
            for r in candidates:
                if len(chosen) >= per_category: break
                if r not in chosen: chosen.append(r)
            selected.extend(r['product_id'] for r in chosen)
        return selected

    def neighbors(self, pid):
        target = self.keywords[pid]
        eligible = [r for r in self.bank.values() if r['product_id'] != pid
                    and r['category'] == target['category']
                    and r['features']['gender'] == target['features']['gender']]
        if len(eligible) < 2:
            raise ValueError('Two same-category, same-gender references required')
        chosen = []
        for modality in ('image', 'text'):
            scores = [(float(np.dot(self.vectors[modality][pid], self.vectors[modality][r['product_id']])), r['product_id'])
                      for r in eligible if r['product_id'] not in {x['product_id'] for x in chosen}]
            score, ref_id = sorted(scores, key=lambda x: (-x[0], x[1]))[0]
            chosen.append({'product_id': ref_id, 'modality': modality, 'cosine_similarity': score,
                           'image_ids': [r['image_id'] for r in example_images(self.images[ref_id])]})
        return chosen

    def prompt(self, pid):
        neighbors = self.neighbors(pid)
        examples = [{'record': self.bank[n['product_id']], 'source': self.source[n['product_id']],
                     'images': [im['path'] for im in example_images(self.images[n['product_id']])]} for n in neighbors]
        prompt = build_prompt(self.keywords[pid], self.source[pid],
                              [im['path'] for im in self.images[pid]], examples)
        return prompt, neighbors

    def result(self, pid, response, metadata):
        original = self.keywords[pid]
        merged = validate_response(response, original)
        record = copy.deepcopy(original)
        record.update(product_status=response['product_status'], product_reason=response['product_reason'],
                      outside_schema_reasons=response.get('outside_schema_reasons', {}), llm_metadata=metadata)
        if merged is None:
            record['status'] = 'needs_review'
            return record
        for feature, value in response['features'].items():
            unresolved = value == 'outside_schema'
            record['feature_metadata'][feature] = {
                'status': 'outside_schema' if unresolved else 'assigned', 'source': 'llm',
                'strategy': 'structured_output',
                'evidence': {'call_id': metadata['call_id'], **({'reason': response['outside_schema_reasons'][feature]} if unresolved else {})}}
            if not unresolved:
                record['features'][feature] = value
        record['status'] = 'pending' if response.get('outside_schema_reasons') else 'ready'
        if any(record['features'].get(k) != v for k, v in original['features'].items()):
            raise ValueError('Keyword assignment changed')
        return record

    def add_reference(self, record):
        if record['status'] != 'ready': return
        poses = {image['pose'] for image in self.images[record['product_id']]}
        if not {'id_gridfs_1', 'id_gridfs_3'} <= poses:
            return False
        self.check_reference(record)
        self.bank[record['product_id']] = record
        return True
