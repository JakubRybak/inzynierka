import argparse
from pathlib import Path

import pandas as pd


TEE_TERMS = r"(?:t[ -]?shirts?|tees?(?:[ -]shirts?)?)"
COLLAR_TERMS = r"col{1,2}ar"
KEYWORDS = {
    "t-shirts": r"\b(?:t[ -]?shirts?|tees?)\b",
    "polos": (
        rf"\b(?:polos?|{COLLAR_TERMS}(?:ed)?[ -]+{TEE_TERMS}"
        rf"|{TEE_TERMS}\s+with\s+(?:a\s+)?{COLLAR_TERMS})\b"
    ),
    "tank-tops": (
        r"\b(?:tank[ -]?tops?|tanks|(?:muscle|racerback)[ -]tanks?"
        r"|cami(?:sole)?s?|tube[ -]tops?|singlets?)\b"
    ),
    "bodysuits": r"\b(?:body[ -]?suits?|leotards?)\b",
    "shirts": r"(?<!\bt[ -])\b(?:shirts?|koszul[aeęiy]|camisas?)\b",
    "blouses": r"\b(?:blouses?|bluzk[aeęią]|blusas?)\b",
    "classic-coats": r"\b(?:coats?|overcoats?|topcoats?|pea[ -]?coats?|parkas?|płaszcze?|abrigos?)\b",
    "trench-coats": r"\b(?:trench(?:[ -]+coats?)?|trencz(?:e|a)?|gabardinas?)\b",
    "jackets": r"\b(?:jackets?|wind[ -]?breakers?|anoraks?|kurtk[aięą]|chaquetas?)\b",
    "bombers": r"\b(?:bombers?|bomberk[aięą])\b",
    "vests": r"\b(?:vests?|gilets?|bodywarmers?|kamizelk[aięą]|chalecos?)\b",
    "trousers": r"\b(?:trousers|slacks|(?:dress|suit|office|leather|linen)[ -]pants)\b",
    "cargo-pants": r"\b(?:cargo[ -]+(?:pants|trousers|joggers)|pantalones?[ -]+cargo|bojówk[ai])\b",
    "sweatpants-and-lounge-pants": r"\b(?:sweat[ -]?pants|joggers|lounge[ -]+pants|dresy)\b",
    "jeans": r"\b(?:jeans|denims|dżinsy|vaqueros)\b",
    "shorts": r"\b(?:shorts|bermudas?|hot[ -]?pants|szorty|spodenki)\b",
}


def main():
    parser = argparse.ArgumentParser(description="Export clothing queries from an Amazon ESCI Parquet file.")
    parser.add_argument("input", type=Path, help="Path to the source Parquet file")
    parser.add_argument("output", type=Path, help="Path to the output CSV file")
    parser.add_argument(
        "--category", choices=KEYWORDS, default="t-shirts", help="Keyword group (default: t-shirts)"
    )
    args = parser.parse_args()

    if args.input.resolve() == args.output.resolve():
        parser.error("The input and output paths must be different.")

    queries = pd.read_parquet(args.input, columns=["query"])["query"]
    matches = queries.str.contains(KEYWORDS[args.category], case=False, na=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    queries[matches].drop_duplicates().to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
