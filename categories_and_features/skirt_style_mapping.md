# Mapowanie sylwetki i typu spódnicy

Dotyczy kategorii `Skirts`. Dawne `skirt_style` zastępują `skirt_silhouette` i `skirt_type`.

## Sylwetka (`skirt_silhouette`, single choice)

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Fitted` | Dopasowana do ciała, również ołówkowa i bodycon (`pencil`, `bodycon`, `fitted`, `slim-fit`). |
| `Straight` | Zasadniczo prosta, bez wymogu obcisłości (`straight skirt`, `straight-fit`, `column`). |
| `A-Line` | Rozszerzająca się ku dołowi (`a-line`, `flared`, `skater`, `circle skirt`). |
| `Other` | Rozpoznana sylwetka poza powyższymi klasami, np. kokonowa lub nietypowa konstrukcja przestrzenna. |

Znaczenie sylwetek jest zgodne z `Dresses`. Nie mapujemy automatycznie prostej spódnicy do dopasowanej. Samo plisowanie, falbany, warstwy lub asymetria nie przesądzają o sylwetce.

## Typ (`skirt_type`, multi choice)

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Pleated` | Plisowana konstrukcja spódnicy (`pleated`, `accordion-pleated`, `knife-pleated`, `box-pleated`, `plissé`); pojedyncza zakładka nie przesądza o typie. |
| `Wrap` | Kopertowa konstrukcja z zachodzącymi na siebie panelami (`wrap skirt`, `pareo`, `sarong`, `overlap front`). |
| `Asymmetric` | Asymetryczna konstrukcja lub dół (`asymmetric`, `high-low hem`, `handkerchief hem`). |
| `Tiered` | Konstrukcja z wyraźnych pięter lub warstw (`tiered`, `tiered panels`, `tiered overskirt`). |
| `Ruffled` | Konstrukcja z falbanami (`ruffled`, `ruffle hem`, `flounces`). |
| `Other` | Brak któregokolwiek z nazwanych szczególnych typów; wartość występuje samodzielnie. |

Wybieramy wszystkie potwierdzone typy, bez powtórzeń. Możliwe są np. `["Pleated", "Wrap"]` i `["Wrap", "Asymmetric"]`. Samo drapowanie nie oznacza automatycznie `Wrap` ani `Asymmetric`. Nie przypisujemy typu na podstawie samego materiału lub długości.

## Pozostałe cechy

- `gender`, `colors`, `main_composition`, `pattern`: zasady jak w `Tops` i `Dresses`; skład dotyczy jednej głównej części ubrania i sumuje się do 100%.
- `length`: `Mini`, `Midi`, `Maxi`, single choice. Źródłowe `MID LENGTH SKIRTS` należy do grupy midi.
- `rise`: `High-Rise`, `Mid-Rise`, `Low-Rise`, single choice. LLM rozstrzyga wysokość stanu na podstawie opisu i zdjęć; brak dosłownego określenia w tekście nie przesądza o wyniku.
- `full_composition_text` nie jest cechą docelową.
