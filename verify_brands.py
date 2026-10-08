"""
Weryfikacja zachowania otwartej detekcji marki (Open Brand Detection)
na kluczowych zapytaniach z markami oraz potencjalnymi fałszywymi markami (np. 'california', 'polo', 'oxford').
"""
import os
import json
from google import genai
from evaluate_gemini_extraction import step_1_classify_category, step_2_extract_attributes

TEST_QUERIES = [
    # Rzeczywiste marki:
    ("north face jacket womens", "The North Face"),
    ("32 degrees jackets for women", "32 Degrees"),
    ("yellow champion hoodie", "Champion"),
    ("track jacket men venum", "Venum"),
    ("g star hoodies for men", "G-Star"),
    ("port authority cardigan", "Port Authority"),
    ("jerzees long sleeve t shirt", "Jerzees"),
    ("nautica polo shirts for men", "Nautica"),
    ("dewalt shirt for men", "DeWalt"),
    ("carhartt double front pants for men", "Carhartt"),
    ("adidas shoes men", "Adidas"),
    # Potencjalne fałszywe marki (False Positive traps):
    ("california sweatshirt for women", None),
    ("golf polo slim fit", None),
    ("mens navy and gray oxford shirt", None),
    ("cowboy boots women", None),
]

def main():
    project_id = "project-3a86f100-1aae-4780-84b"
    location = "us"
    client = genai.Client(vertexai=True, project=project_id, location=location)

    print("=" * 90)
    print(" SZCZEGÓŁOWA WERYFIKACJA DETEKCJI MAREK (OPEN BRAND EXTRACTION)")
    print("=" * 90)

    for query, expected_brand in TEST_QUERIES:
        cat = step_1_classify_category(client, query)
        extraction = step_2_extract_attributes(client, query, cat) if cat != "None" else {}
        attrs = extraction.get("extracted_attributes", {})
        residual = extraction.get("residual_text", "")
        extracted_brand = attrs.get("brand")

        # Ocena dopasowania marki
        if expected_brand is None:
            status = "✅ Brak marki (poprawnie)" if extracted_brand is None else f"❌ FP! Wykryto '{extracted_brand}'"
        else:
            if extracted_brand and extracted_brand.lower().replace("-", " ").replace("the ", "").strip() == expected_brand.lower().replace("-", " ").replace("the ", "").strip():
                status = f"✅ Wykryto markę: '{extracted_brand}'"
            else:
                status = f"❌ Oczekiwano: '{expected_brand}', Wykryto: '{extracted_brand}'"

        print(f"Q: \"{query:40s}\" | Kat: {cat:20s} | {status} | Resztka: \"{residual}\"")

if __name__ == "__main__":
    main()
