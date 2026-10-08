"""
Test zachowania pipeline'u dla zapytań slangowych/eponimicznych (EN)
oraz zapytań w języku polskim (PL), z zachowaniem angielskich promptów i schematów Pydantic.
"""
import json
import time
from google import genai
from evaluate_gemini_extraction import step_1_classify_category, step_2_extract_attributes

TEST_CASES = [
    # --- 1. JĘZYK POLSKI (PL) ---
    # A. Czyste eponimy (marka = nazwa typu buta/ubrania)
    {"lang": "PL", "group": "Eponim PL", "query": "czarne timberlandy", "note": "Potoczna nazwa butów traperów (Timberland)"},
    {"lang": "PL", "group": "Eponim PL", "query": "biale adidasy damskie", "note": "W polskim 'adidasy' = buty sportowe"},
    {"lang": "PL", "group": "Eponim PL", "query": "conversy za kostke", "note": "Conversy = trampki Converse wysokie"},

    # B. Test sprzeczności kulturowej
    {"lang": "PL", "group": "Sprzeczność PL", "query": "adidasy nike do biegania", "note": "Pospolicenie 'adidasy' połączone z marką konkurencji Nike"},

    # C. Tłumaczenie polskich cech do angielskiego schematu Pydantic
    {"lang": "PL", "group": "Cross-lingual PL", "query": "ciepla zimowa kurtka north face damska", "note": "Puchowa/zimowa kurtka The North Face"},
    {"lang": "PL", "group": "Cross-lingual PL", "query": "czerwona meska bluza z kapturem champion", "note": "Bluza z kapturem Champion + cechy"},
    {"lang": "PL", "group": "Cross-lingual PL", "query": "czarny golf z welny", "note": "Pułapka słowna: 'golf' jako dekolt Turtleneck z wełny"},
    {"lang": "PL", "group": "Cross-lingual PL", "query": "elegancka czarna sukienka na wesele", "note": "Sukienka + okazja na wesele (wedding)"},

    # --- 2. JĘZYK ANGIELSKI (EN) ---
    # A. Eponimy obuwia (slang i skróty brandowe)
    {"lang": "EN", "group": "Eponim EN Obuwie", "query": "wheat timbs", "note": "Amerykański slang miejski na żółte trapery Timberland"},
    {"lang": "EN", "group": "Eponim EN Obuwie", "query": "high top chucks", "note": "Slang na trampki Converse Chuck Taylor wysokie"},
    {"lang": "EN", "group": "Eponim EN Obuwie", "query": "leather docs", "note": "Docs = glany/botki Dr. Martens"},
    {"lang": "EN", "group": "Eponim EN Obuwie", "query": "womens classic uggs", "note": "Uggs = buty zimowe wsuwane UGG"},
    {"lang": "EN", "group": "Eponim EN Obuwie", "query": "summer birks", "note": "Birks = sandały/klapki Birkenstock"},

    # B. Eponimy odzieży
    {"lang": "EN", "group": "Eponim EN Odzież", "query": "vintage levis", "note": "Levis = dżinsy Levi's bez słowa 'jeans'"},
    {"lang": "EN", "group": "Eponim EN Odzież", "query": "carhartt double knee", "note": "Popularne spodnie robocze Carhartt bez słowa 'pants'"}
]

def main():
    project_id = "project-3a86f100-1aae-4780-84b"
    location = "us"
    client = genai.Client(vertexai=True, project=project_id, location=location)

    print("=" * 115)
    print(" TEST ZAPYTAŃ POTOCZNYCH (SLANG EN) ORAZ ZAPYTAŃ POLSKICH (CROSS-LINGUAL PL -> EN SCHEMA)")
    print(" Model: gemini-3.5-flash-lite | Czysty prompt (zero leaków)")
    print("=" * 115)

    results = []
    for idx, item in enumerate(TEST_CASES, 1):
        q = item["query"]
        lang = item["lang"]
        group = item["group"]
        note = item["note"]

        t0 = time.time()
        cat = step_1_classify_category(client, q)
        t1 = time.time()
        s1_ms = (t1 - t0) * 1000

        s2_ms = 0
        attrs = {}
        residual = ""
        if cat != "None":
            t2 = time.time()
            extraction = step_2_extract_attributes(client, q, cat)
            t3 = time.time()
            s2_ms = (t3 - t2) * 1000
            attrs = extraction.get("extracted_attributes", {})
            residual = extraction.get("residual_text", "")

        total_ms = s1_ms + s2_ms

        print(f"\n[{idx:2d}/15] [{lang}] [{group:18s}] Query: \"{q}\"")
        print(f"       Opis kontekstu : {note}")
        print(f"       -> Kategoria   : [{cat}] (S1: {s1_ms:.0f}ms)")
        print(f"       -> Marka       : {attrs.get('brand', 'None')}")
        print(f"       -> Cechy       : {json.dumps(attrs, ensure_ascii=False)}")
        print(f"       -> Resztka     : \"{residual}\" (S2: {s2_ms:.0f}ms | Total: {total_ms:.0f}ms)")

        results.append({
            "idx": idx,
            "query": q,
            "lang": lang,
            "group": group,
            "note": note,
            "category": cat,
            "brand": attrs.get("brand"),
            "attributes": attrs,
            "residual_text": residual,
            "s1_ms": s1_ms,
            "s2_ms": s2_ms,
            "total_ms": total_ms
        })

    with open("slang_and_polish_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n" + "=" * 115)
    print(f"Zakończono testy 15 zapytań. Wyniki zapisano do slang_and_polish_results.json")
    print("=" * 115)

if __name__ == "__main__":
    main()
