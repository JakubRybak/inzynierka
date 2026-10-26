"""Render the curated reference JSONL as Markdown without changing annotations."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / 'poc/feature_extraction/reference'


def render():
    records = [json.loads(line) for line in (REFERENCE / 'products.jsonl').read_text().splitlines()]
    with (ROOT / 'data/processed/fashiongen/products_train.csv').open(newline='') as stream:
        source = {row['product_id']: row for row in csv.DictReader(stream)}
    lines = [
        '# Przykłady referencyjne — 60 produktów', '',
        'Po 20 produktów z każdej kategorii, wybranych z próbki 900 produktów. '
        'Uzupełnienia przypisał Codex po przejrzeniu opisów i wszystkich dostępnych zdjęć. '
        'Nie są oznaczone jako zatwierdzone przez użytkownika.', '',
        'Wartości z preprocessingu pozostają bez zmian. Źródło `manual` '
        'oznacza uzupełnienie na podstawie zdjęć i opisu. '
        'Fit i długość góry są ocenami orientacyjnymi; długość sukienek pochodzi z kategorii źródłowej.', '',
        'Przyjęto: wyraźna grafika lub napis bez osobnej klasy wzoru → Other; '
        'motyw kwiatowy → Floral; sam melanż, prążkowana faktura i szwy → Solid. '
        'Ramiączka pośredniej szerokości → Other. Są to robocze interpretacje etykiet.', '',
    ]
    category = None
    for record in records:
        if record['category'] != category:
            category = record['category']
            lines.extend([f'## {category}', ''])
        original = source[record['product_id']]
        lines.extend([f"### {record['product_id']} — {original['name']}", '',
                      f"**Marka:** {record['brand']} · **Płeć:** {record['features']['gender']}", '',
                      f"**Opis:** {original['description']}", '',
                      f"**Skład źródłowy:** {original['composition']}", '',
                      '**Wszystkie zdjęcia:**', ''])
        for img in record['images']:
            path = ROOT / img['path']
            if not path.is_file():
                raise FileNotFoundError(path)
            lines.append(f"![{img['image_id']}]({path})")
        lines.extend(['', '**Zdjęcia do przykładu:** ' + ', '.join(record['example_image_ids']) + '.', '',
                      '| Cecha | Wartość | Źródło |', '| --- | --- | --- |'])
        for feature, metadata in record['feature_metadata'].items():
            value = record['features'][feature]
            text = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
            lines.append(f"| `{feature}` | {text} | `{metadata['source']}` |")
        if record['review_notes']:
            lines.extend(['', '**Uwaga:** ' + record['review_notes']])
        lines.extend(['', '---', ''])
    (REFERENCE / 'review.md').write_text('\n'.join(lines))
    print(f'Rendered {len(records)} products to {REFERENCE / "review.md"}')


if __name__ == '__main__':
    render()
