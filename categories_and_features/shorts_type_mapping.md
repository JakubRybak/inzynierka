# Mapowanie typu szortów (`shorts_type`)

Dotyczy kategorii `Shorts` (źródłowo `input_category = SHORTS`, `input_subcategory = SHORTS`). Multi choice, bez powtórzeń; `Other` samodzielnie.

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Denim` | Szorty jeansowe (`denim shorts`, `jean shorts`, `jorts`). Sam skład bawełniany nie wystarcza. |
| `Cargo` | Konstrukcja z charakterystycznymi kieszeniami cargo. Same zwykłe kieszenie nie wystarczają. |
| `Sweatshorts` | Konstrukcja szortów dresowych (`sweatshorts`, `sweat shorts`). Sam jersey ani elastyczny pas nie wystarczają. |
| `Athletic` | Konstrukcja sportowa, np. biegowa lub koszykarska (`running shorts`, `basketball shorts`, `athletic shorts`). Sam elastyczny pas nie wystarcza. |
| `Tailored` | Elegancka, modelowana konstrukcja szortów (`tailored shorts`, konstrukcja garniturowa). Nie wynika automatycznie ze sztywnego pasa. |
| `Other` | Brak któregokolwiek z nazwanych szczególnych typów. |

Wybieramy wszystkie potwierdzone typy, np. `["Denim", "Cargo"]`. Bermudy opisuje `length = Long`, nie osobna wartość typu.

## Pozostałe cechy `Shorts`

- `gender`: single choice.
- `colors`: 1–2 różne kolory albo samo `Multicolor`; słownik wspólny z `Tops`, `Dresses` i `Skirts`.
- `main_composition`: jeden skład głównej części z procentami sumującymi się do 100%; zasady jak w pozostałych dopracowanych kategoriach.
- `pattern`: multi choice; `Solid` i `Other` samodzielnie. Konkretne wzory można łączyć; nie dodajemy `Other` za logo przy nazwanym wzorze.
- `fit`: `Slim`, `Regular`, `Relaxed`, single choice.
- `waistband_type`: `Structured`, `Elasticized`, `Other`, single choice; definicje w `waistband_type_mapping.md`.
- `length`: `Short`, `Mid-Length`, `Long`, single choice. Odpowiednio krótkie szorty wysoko na udzie, standardowe do połowy uda oraz długie w okolice kolan lub tuż poniżej.
- `rise`: `High-Rise`, `Mid-Rise`, `Low-Rise`, single choice.
- `full_composition_text` nie jest cechą docelową.
