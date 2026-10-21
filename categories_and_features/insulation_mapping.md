# Mapowanie konstrukcji ocieplenia (`insulation`)

Multi choice we wszystkich pięciu kategoriach `Jackets & Coats`. `Unpadded` i `Other` występują samodzielnie. Lista bez powtórzeń.

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Unpadded` | Bez dodatkowego ocieplającego wypełnienia lub podszewki. Zwykła podszewka materiałowa jest dozwolona. |
| `Padded` | Wypełnienie puchowe albo syntetyczne (`down-filled`, `feather-filled`, `polyester fill`, `padding`). |
| `Fur Lined` | Ocieplająca podszewka z futra lub kożucha, również sztucznego (`fur-lined`, `shearling-lined`, `faux-fur lining`). |
| `Fleece Lined` | Ocieplająca podszewka z polaru, sherpa lub podobnego materiału (`fleece-lined`, `sherpa-lined`, `borg lining`). |
| `Other` | Inna rozpoznana konstrukcja dodatkowego ocieplenia. |

- Dopuszczamy współwystępowanie, np. `["Padded", "Fur Lined"]`.
- Zwykła podszewka z wiskozy, poliestru lub bawełny nie oznacza ocieplenia.
- Futrzane obszycie kaptura, mankietu lub kołnierza nie oznacza `Fur Lined`.
- Samo pikowanie nie potwierdza `Padded`; potrzebne jest rozpoznanie wypełnienia.
- Sam futrzany lub wełniany materiał zewnętrzny nie oznacza podszewki ocieplającej. Opisuje go `main_composition`.
- Cecha nie określa grubości ubrania ani temperatury użytkowania. Dawne `Lightweight`, `Midweight`, `Shearling` nie są wartościami docelowego słownika.
