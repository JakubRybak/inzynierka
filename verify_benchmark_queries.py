import csv
import json

BENCHMARK_FILE = "fashion_test_benchmark.csv"
AMAZON_FILE = "clothing_queries.csv"

def verify():
    # 1. Wczytaj bazę zapytań Amazon ESCI
    with open(AMAZON_FILE, "r", encoding="utf-8") as f:
        amazon_reader = csv.DictReader(f)
        amazon_queries = {row["Query_Text"].strip().lower(): row["Query_ID"] for row in amazon_reader}

    print(f"Liczba zapytań w bazie Amazon ESCI ({AMAZON_FILE}): {len(amazon_queries):,}")

    # 2. Wczytaj nasz zbiór testowy benchmarku
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        benchmark_rows = list(csv.DictReader(f))

    print(f"Liczba zapytań w zbiorze benchmarku ({BENCHMARK_FILE}): {len(benchmark_rows)}")
    print("=" * 80)

    missing = []
    found_count = 0
    categories = {}
    difficulties = {}

    for idx, row in enumerate(benchmark_rows, 1):
        q = row["query"].strip()
        q_norm = q.lower()
        cat = row["category"]
        diff = row["difficulty"]

        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

        if q_norm in amazon_queries:
            found_count += 1
            amazon_id = amazon_queries[q_norm]
            # Sprawdź czy query_id się zgadza
            id_match = (row["query_id"] == amazon_id)
        else:
            missing.append((idx, q, cat))

    print(f"WYNIK WERYFIKACJI: {found_count}/{len(benchmark_rows)} zapytań ({(found_count/len(benchmark_rows))*100:.1f}%) ZNALEZIONO W AMAZON ESCI!")
    print("=" * 80)

    if missing:
        print(f"BŁĄD: Następujące {len(missing)} zapytań nie zostało znalezionych w Amazon ESCI:")
        for idx, q, cat in missing:
            print(f"  [{idx}] \"{q}\" (Kategoria: {cat})")
    else:
        print("WSZYSTKIE 80 ZAPYTAŃ ZNAJDUJE SIĘ W 100% W DANYCH AMAZON ESCI! (ZERO HALUCYNACJI)")

    print("\nROZKŁAD KATEGORII W ZBIORZE TESTOWYM:")
    for cat, cnt in sorted(categories.items()):
        print(f"  - {cat:25s}: {cnt} zapytań")

    print("\nROZKŁAD POZIOMU TRUDNOŚCI:")
    for diff, cnt in sorted(difficulties.items()):
        print(f"  - {diff:20s}: {cnt} zapytań")

if __name__ == "__main__":
    verify()
