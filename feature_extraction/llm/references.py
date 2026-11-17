"""Retrieve distinct image/text neighbors from the growing reference bank."""
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from ..storage import digest
from ..schema import load_schemas
from ..validation import validate_features

SCHEMAS, _ = load_schemas()


def example_images(images):
    by_pose = {row['pose']: row for row in images}
    return [by_pose[pose] for pose in ('id_gridfs_1', 'id_gridfs_3')]


class ReferenceBank:
    def __init__(self, records, source, images, embeddings_folder, target_ids):
        self.source, self.images, self.bank = source, images, {}
        self._bucket_ids = {}
        self._bucket_matrices = {}
        self._bucket_dirty = set()
        folder = Path(embeddings_folder)
        manifest = json.loads((folder / 'manifest.json').read_text())
        if not manifest['complete']:
            raise ValueError('Incomplete embedding export')
        self.vectors = {}
        needed = set(target_ids) | {row['product_id'] for row in records}
        for modality in ('image', 'text'):
            rows = {r['product_id']: r for r in pq.read_table(folder / f'{modality}.parquet').to_pylist()}
            if needed - rows.keys():
                raise ValueError(f'Missing {modality} embeddings for {sorted(needed - rows.keys())[:5]}')
            vectors = {}
            for pid in needed:
                row = rows[pid]
                content = (Path(images[pid][0]['path']).read_bytes() if modality == 'image'
                           else source[pid]['description'].encode())
                if digest(content) != row['input_sha256']:
                    raise ValueError(f'Stale {modality} embedding for {pid}')
                vector = np.asarray(row['embedding'], dtype=np.float32)
                if not np.isfinite(vector).all() or not np.isclose(np.linalg.norm(vector), 1, atol=1e-5):
                    raise ValueError(f'Invalid normalized embedding for {pid}')
                vectors[pid] = vector
            self.vectors[modality] = vectors
        for record in records:
            if not self.add(record):
                raise ValueError(f'Invalid seed reference: {record["product_id"]}')

    def add(self, record):
        pid = record['product_id']
        if record['status'] != 'ready' or record.get('product_status', 'ok') != 'ok':
            return False
        rules = SCHEMAS[(record['section'], record['category'])]
        if set(record['features']) != set(rules) or any(v == 'outside_schema' for v in record['features'].values()):
            raise ValueError(f'Incomplete reference: {pid}')
        validate_features(record['features'], rules, complete=True)
        if not {'id_gridfs_1', 'id_gridfs_3'} <= {image['pose'] for image in self.images[pid]}:
            return False
        bucket = (record['category'], record['features']['gender'])
        if pid not in self.bank:
            self._bucket_ids.setdefault(bucket, []).append(pid)
        self.bank[pid] = record
        self._bucket_dirty.add(bucket)
        return True

    def _ensure_bucket(self, bucket):
        if bucket in self._bucket_dirty or bucket not in self._bucket_matrices:
            pids = [pid for pid in self._bucket_ids.get(bucket, []) if pid in self.bank]
            self._bucket_ids[bucket] = pids
            if pids:
                self._bucket_matrices[bucket] = {
                    modality: np.vstack([self.vectors[modality][pid] for pid in pids])
                    for modality in ('image', 'text')
                }
            else:
                self._bucket_matrices[bucket] = {}
            self._bucket_dirty.discard(bucket)
        return self._bucket_ids.get(bucket, []), self._bucket_matrices.get(bucket, {})

    def examples(self, target):
        pid = target['product_id']
        bucket = (target['category'], target['features']['gender'])
        pids, matrices = self._ensure_bucket(bucket)
        eligible_count = len(pids) - (1 if pid in self.bank and self.bank[pid]['category'] == bucket[0]
                                      and self.bank[pid]['features']['gender'] == bucket[1] else 0)
        if eligible_count < 2:
            raise ValueError(f'Two same-category/gender references required for {pid}')
        neighbors, examples = [], []
        used = {pid}
        for modality in ('image', 'text'):
            raw_scores = matrices[modality] @ self.vectors[modality][pid]
            best_key = None
            best_score = None
            best_ref = None
            for idx, ref_id in enumerate(pids):
                if ref_id in used:
                    continue
                score = float(raw_scores[idx])
                key = (-score, ref_id)
                if best_key is None or key < best_key:
                    best_key = key
                    best_score = score
                    best_ref = ref_id
            used.add(best_ref)
            selected_images = example_images(self.images[best_ref])
            neighbors.append({'product_id': best_ref, 'modality': modality, 'cosine_similarity': best_score,
                              'image_ids': [row['image_id'] for row in selected_images]})
            examples.append({'record': self.bank[best_ref], 'source': self.source[best_ref],
                             'images': [row['path'] for row in selected_images]})
        return examples, neighbors
