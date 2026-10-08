import re
import pandas as pd

LOCAL_FILE = "shopping_queries_dataset_examples.parquet"

# Nasze dotychczasowe słowa kluczowe (z export_clothing_queries.py)
EXPLICIT_CLOTHING_KEYWORDS = [
    r"\bcloth\b", r"\bclothing\b", r"\bapparel\b", r"\bwear\b", r"\boutfit\b", r"\bgarment\b",
    r"\bshirt\b", r"\bt-shirt\b", r"\btshirt\b", r"\btee\b", r"\btop\b", r"\btops\b", r"\bblouse\b",
    r"\bhoodie\b", r"\bhoodies\b", r"\bsweater\b", r"\bsweaters\b", r"\bsweatshirt\b", r"\bcardigan\b",
    r"\btank top\b", r"\bv-neck\b", r"\bpolo\b", r"\btunic\b", r"\bvest\b",
    r"\bpants\b", r"\btrousers\b", r"\bjeans\b", r"\bshorts\b", r"\bleggings\b", r"\bjoggers\b",
    r"\bsweatpants\b", r"\bskirt\b", r"\bskirts\b", r"\btights\b", r"\bcapris\b",
    r"\bdress\b", r"\bdresses\b", r"\bgown\b", r"\bsuit\b", r"\bsuits\b", r"\bblazer\b",
    r"\bjumpsuit\b", r"\bromper\b", r"\btuxedo\b",
    r"\bjacket\b", r"\bjackets\b", r"\bcoat\b", r"\bcoats\b", r"\bparka\b", r"\bwindbreaker\b",
    r"\braincoat\b", r"\bponcho\b", r"\banorak\b",
    r"\bunderwear\b", r"\bbra\b", r"\bbras\b", r"\bpanties\b", r"\bboxers\b", r"\bbriefs\b",
    r"\bsocks\b", r"\bpajamas\b", r"\bpyjamas\b", r"\bnightgown\b", r"\brobe\b", r"\blingerie\b",
    r"\bswimsuit\b", r"\bbikini\b", r"\bswimwear\b", r"\btrunks\b",
    r"\bshoes\b", r"\bshoe\b", r"\bsneakers\b", r"\bboots\b", r"\bboot\b", r"\bsandals\b",
    r"\bheels\b", r"\bhigh heels\b", r"\bslippers\b", r"\bloafers\b", r"\bflats\b", r"\bcleats\b",
    r"\bhat\b", r"\bhats\b", r"\bcap\b", r"\bcaps\b", r"\bscarf\b", r"\bgloves\b", r"\bmittens\b",
    r"\bbelt\b", r"\bbelts\b", r"\btie\b", r"\bbeanie\b"
]
EXPLICIT_REGEX = re.compile("|".join(EXPLICIT_CLOTHING_KEYWORDS), re.IGNORECASE)

# 1. Znane marki odzieżowe / obuwnicze
FASHION_BRANDS = [
    r"\bnike\b", r"\badidas\b", r"\blululemon\b", r"\bgymshark\b", r"\blevi'?s\b", r"\bunder armour\b",
    r"\bpatagonia\b", r"\bcarhartt\b", r"\bcalvin klein\b", r"\btommy hilfiger\b", r"\bvans\b",
    r"\bconverse\b", r"\bnew balance\b", r"\bpuma\b", r"\breebok\b", r"\bcolumbia\b", r"\bnorth face\b",
    r"\bchampion\b", r"\bhollister\b", r"\bamerican eagle\b", r"\bdoc martens\b", r"\bdr martens\b",
    r"\bbirkenstock\b", r"\bcrocs\b", r"\bspanx\b", r"\bvictoria'?s secret\b", r"\btimberland\b",
    r"\bskims\b", r"\bzara\b", r"\bh&m\b", r"\basos\b", r"\bshein\b"
]
BRANDS_REGEX = re.compile("|".join(FASHION_BRANDS), re.IGNORECASE)

# 2. Okazje, estetyka, styl, cechy bez słowa kluczowego
AESTHETIC_OCCASIONS = [
    r"\bwedding guest\b", r"\bcocktail\b", r"\bblack tie\b", r"\bformal\b", r"\bcasual\b",
    r"\bprom\b", r"\bmaternity\b", r"\bplus size\b", r"\boversized\b", r"\by2k\b", r"\bvintage\b",
    r"\bretro\b", r"\bgrunge\b", r"\bcottagecore\b", r"\bboho\b", r"\bworkout\b", r"\bgym\b",
    r"\bathletic\b", r"\bsexy\b", r"\belegant\b", r"\bstreetwear\b", r"\bsummer\b", r"\bwinter\b"
]
AESTHETIC_REGEX = re.compile("|".join(AESTHETIC_OCCASIONS), re.IGNORECASE)

# 3. Specyficzne elementy garderoby / slang, które mogły umknąć
MISSED_FASHION_TERMS = [
    r"\bdenim\b", r"\bfleece\b", r"\bcorduroy\b", r"\bcashmere\b", r"\bflannel\b",
    r"\boveralls\b", r"\bbodysuit\b", r"\bonesie\b", r"\bkimono\b", r"\bculottes\b",
    r"\bcamisole\b", r"\bcami\b", r"\bhalter\b", r"\bcardigans\b", r"\blegging\b",
    r"\bhoody\b", r"\bsweats\b", r"\bslip\b", r"\bchinos\b", r"\bjogger\b",
    r"\bparkas\b", r"\bwind breakers\b", r"\bpeacoat\b", r"\btrench\b", r"\btights\b"
]
MISSED_REGEX = re.compile("|".join(MISSED_FASHION_TERMS), re.IGNORECASE)

def main():
    print("Wczytywanie zapytań US...")
    df = pd.read_parquet(LOCAL_FILE)
    df_us = df[df["product_locale"] == "us"]
    unique_queries = df_us[["query"]].drop_duplicates().copy()
    unique_queries["query_clean"] = unique_queries["query"].astype(str)

    # Odrzucamy znaki azjatyckie
    asian_regex = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")
    unique_queries = unique_queries[~unique_queries["query_clean"].str.contains(asian_regex)]
    
    total_queries = len(unique_queries)

    # Nasze dotychczasowe dopasowanie
    has_explicit = unique_queries["query_clean"].str.contains(EXPLICIT_REGEX)
    explicit_df = unique_queries[has_explicit]
    non_explicit_df = unique_queries[~has_explicit].copy()

    print(f"Łącznie unikalnych zapytań US: {total_queries:,}")
    print(f"Dopasowane słowami kluczowymi (wybrane wcześniej): {len(explicit_df):,} ({len(explicit_df)/total_queries*100:.2f}%)")
    print(f"Odrzucone (potencjalnie ukryte zapytania): {len(non_explicit_df):,} ({len(non_explicit_df)/total_queries*100:.2f}%)")

    # Weryfikacja odrzuconych zapytań
    has_brand = non_explicit_df["query_clean"].str.contains(BRANDS_REGEX)
    has_aesthetic = non_explicit_df["query_clean"].str.contains(AESTHETIC_REGEX)
    has_missed = non_explicit_df["query_clean"].str.contains(MISSED_REGEX)

    brand_only = non_explicit_df[has_brand]
    aesthetic_only = non_explicit_df[has_aesthetic & ~has_brand]
    missed_only = non_explicit_df[has_missed & ~has_brand & ~has_aesthetic]

    total_hidden_fashion = non_explicit_df[has_brand | has_aesthetic | has_missed]

    print("\n" + "=" * 80)
    print(" WYNIKI ANALIZY BIASU (UKRYTE ZAPYTANIA MODOWE)")
    print("=" * 80)
    print(f"1. Same marki odzieżowe bez rzeczownika (np. 'lululemon', 'nike'): {len(brand_only):,}")
    print(f"2. Okazje, estetyka, przymiotniki (np. 'wedding guest', 'plus size'): {len(aesthetic_only):,}")
    print(f"3. Niszowe elementy / materiały (np. 'denim', 'overalls', 'fleece'):   {len(missed_only):,}")
    print("-" * 80)
    print(f"RAZEM 'ukrytych' zapytań o modę pominiętych przez filtr: {len(total_hidden_fashion):,} (ok. {len(total_hidden_fashion)/total_queries*100:.2f}% wszystkich zapytań)")
    print(f"Prawdziwa liczba zapytań o modę w datasecie: ok. {len(explicit_df) + len(total_hidden_fashion):,} (~{(len(explicit_df) + len(total_hidden_fashion))/total_queries*100:.2f}%)")
    print("=" * 80)

    print("\n Przykłady zapytań o SAME MARKI MODOWE (bez słów typu 'spodnie/buty'):")
    for q in brand_only["query_clean"].sample(min(10, len(brand_only)), random_state=42):
        print(f"  - {q}")

    print("\n Przykłady zapytań o OKAZJE / STYL / CECHY (bez nazwy kategorii):")
    for q in aesthetic_only["query_clean"].sample(min(10, len(aesthetic_only)), random_state=42):
        print(f"  - {q}")

    print("\n Przykłady zapytań z MATERIAŁAMI / SPECYFICZNYMI KROJAMI:")
    for q in missed_only["query_clean"].sample(min(10, len(missed_only)), random_state=42):
        print(f"  - {q}")

if __name__ == "__main__":
    main()
