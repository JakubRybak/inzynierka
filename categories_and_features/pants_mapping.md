# Mapowanie kategorii i cech `Pants`

## Kategorie źródłowe

| Kategoria docelowa | `input_category` | `input_subcategory` |
| :--- | :--- | :--- |
| `Trousers` | `PANTS` | `TROUSERS`, `LEATHER PANTS` |
| `Cargo Pants` | `PANTS` | `CARGO PANTS` |
| `Sweatpants & Lounge Pants` | `PANTS` | `SWEATPANTS`, `LOUNGE PANTS` |
| `Jeans` | `JEANS` | `JEANS` |

Nie tworzymy osobnej kategorii skórzanych spodni; ich skład opisuje `main_composition`. `LEGGINGS` pozostają poza zakresem.

## Cechy

- `gender`, `colors`, `main_composition`, `pattern`: te same zasady jak w pozostałych dopracowanych działach. Skład dotyczy jednej głównej części i sumuje się do 100%. `pattern` jest multi choice; `Solid` i `Other` samodzielnie, bez dodawania `Other` za logo przy nazwanym wzorze.
- `fit`: `Skinny`, `Slim`, `Regular`, `Relaxed`, single choice; dopasowanie w biodrach i udach. Definicje: `fit_mapping.md`.
- `leg_shape`: `Straight`, `Tapered`, `Wide-Leg`, `Flared`, single choice; definicje: `leg_shape_mapping.md`.
- `length`: `Cropped`, `Full-Length`, single choice; definicje: `length_mapping.md`.
- `rise`: `High-Rise`, `Mid-Rise`, `Low-Rise`, single choice.
- `waistband_type`: `Structured`, `Elasticized`, `Other`, single choice we wszystkich czterech kategoriach, także `Jeans`; definicje: `waistband_type_mapping.md`.
- `cuff_style`: `Open Hem`, `Elasticized Cuff`, `Zippered Cuff`, `Other`, single choice we wszystkich czterech kategoriach. Przy jednoczesnym ściągaczu i zamku wybieramy `Zippered Cuff`; definicje: `cuff_style_mapping.md`.
- `distressing`: tylko `Jeans`; `Clean`, `Faded`, `Distressed`, single choice, z pierwszeństwem `Distressed` nad `Faded`.
- `full_composition_text` nie jest cechą docelową.

## Przykłady niezależnych cech

- Luźne spodnie zwężane ku kostce: `fit = Relaxed`, `leg_shape = Tapered`.
- Jeansy z gumką w pasie i rozporkiem: `waistband_type = Elasticized`.
- Rozszerzana nogawka ze zwykłym dołem: `leg_shape = Flared`, `cuff_style = "Open Hem"`.
- Nogawka z gumką i zamkiem przy kostce: `cuff_style = "Zippered Cuff"`.
