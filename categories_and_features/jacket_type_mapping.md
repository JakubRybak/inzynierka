# Mapowanie typu kurtki (`jacket_type`)

Multi choice tylko w `Jackets`. Zastępuje dawne `jacket_style`. `Other` występuje samodzielnie, lista bez powtórzeń.

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Biker` | Konstrukcja motocyklowa lub ramoneska (`biker`, `moto`, `motorcycle`, `perfecto`); sam materiał skórzany nie wystarcza. |
| `Trucker` | Konstrukcja trucker, zwykle z parą kieszeni na piersi i charakterystycznymi podziałami (`trucker`, `type III`); sam denim nie wystarcza. |
| `Puffer` | Charakterystyczna przestrzenna konstrukcja kurtki z wypełnieniem (`puffer`, `baffle`); nie każde lekkie pikowanie jest pufferem. |
| `Windbreaker` | Konstrukcja wiatrówki lub lekkiej sportowej kurtki typu shell (`windbreaker`, `windrunner`, `technical shell`, `anorak`). |
| `Utility` | Konstrukcja użytkowa, wojskowa lub robocza z charakterystycznymi kieszeniami (`field jacket`, `utility`, `safari`, `M-65`, `chore jacket`). |
| `Parka` | Rozpoznana konstrukcja parki; nie wynika automatycznie z długości lub kaptura. |
| `Other` | Brak dopasowania do nazwanych szczególnych typów; zastępuje dawną ogólną klasę `Casual`. |

Dopuszczamy np. `["Puffer", "Parka"]` i `["Utility", "Parka"]`. Typ jest niezależny od `fit`, `length`, materiału i cechy `insulation`.
