"""Atomic persistence shared by extraction and embedding jobs."""
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

JSON_COLUMNS = {'features', 'feature_metadata', 'exclusion_reasons',
                'outside_schema_reasons', 'llm_metadata'}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def write_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    temporary.replace(path)


def export_products(folder, records):
    """Keep existing JSONL and Parquet column representations compatible."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    records = list(records)
    if not records:
        write_jsonl(folder / 'products.jsonl', [])
        return
    columns = list(records[0])
    rows = [{k: json.dumps(r[k], ensure_ascii=False, sort_keys=True) if k in JSON_COLUMNS
             else r[k] for k in columns} for r in records]
    table = pa.Table.from_pylist(rows, schema=pa.schema([(k, pa.string()) for k in columns]))
    temporary = folder / 'products.parquet.tmp'
    pq.write_table(table, temporary, compression='zstd')
    temporary.replace(folder / 'products.parquet')
    write_jsonl(folder / 'products.jsonl', records)
