"""Retrieve distinct image/text neighbors from the growing reference bank."""
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from ..storage import digest
from .prompt_builder import CONFIGS


def example_images(images):
    by_pose = {row['pose']: row for row in images}
    return [by_pose[pose] for pose in ('id_gridfs_1', 'id_gridfs_3')]


class ReferenceBank:
    def __init__(self, records, source, images, embeddings_folder, target_ids):
        self.source, self.images, self.bank = source, images, {}
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
        rules = CONFIGS[(record['section'], record['category'])]
        if set(record['features']) != set(rules) or any(v == 'outside_schema' for v in record['features'].values()):
            raise ValueError(f'Incomplete reference: {pid}')
        if not {'id_gridfs_1', 'id_gridfs_3'} <= {image['pose'] for image in self.images[pid]}:
            return False
        self.bank[pid] = record
        return True

    def examples(self, target):
        pid = target['product_id']
        eligible = [r for r in self.bank.values() if r['product_id'] != pid
                    and r['category'] == target['category']
                    and r['features']['gender'] == target['features']['gender']]
        if len(eligible) < 2:
            raise ValueError(f'Two same-category/gender references required for {pid}')
        neighbors, examples = [], []
        used = set()
        for modality in ('image', 'text'):
            scores = [(float(np.dot(self.vectors[modality][pid], self.vectors[modality][r['product_id']])), r['product_id'])
                      for r in eligible if r['product_id'] not in used]
            score, ref_id = sorted(scores, key=lambda item: (-item[0], item[1]))[0]
            used.add(ref_id)
            selected_images = example_images(self.images[ref_id])
            neighbors.append({'product_id': ref_id, 'modality': modality, 'cosine_similarity': score,
                              'image_ids': [row['image_id'] for row in selected_images]})
            examples.append({'record': self.bank[ref_id], 'source': self.source[ref_id],
                             'images': [row['path'] for row in selected_images]})
        return examples, neighbors
