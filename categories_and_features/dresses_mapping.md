# Mapowanie cech `Dresses`

Dokument określa docelowe zasady dla kategorii `Dresses` i ma pierwszeństwo przed starszymi zasadami sukienek w mapowaniach wspólnych. Pozostałe kategorie zachowują obecne zakresy do czasu ich aktualizacji.

Kategorie źródłowe: `input_category = DRESSES`; podkategorie `SHORT DRESSES`, `MID LENGTH DRESSES`, `LONG DRESSES`. Produkt identyfikujemy przez `input_productID`.

## Sylwetka (`dress_silhouette`, single choice)

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Fitted` | Dopasowana do ciała; obejmuje bodycon i etui (`bodycon`, `sheath`, `figure-hugging`, `fitted`). |
| `Straight` | Zasadniczo prosta, również luźna typu shift (`shift`, `straight-cut`, `column`). |
| `A-Line` | Rozszerza się ku dołowi, również z dopasowaną górą (`a-line`, `flared`, `fit-and-flare`, `skater`). |
| `Other` | Rozpoznana sylwetka poza powyższymi klasami, np. kokonowa lub nietypowa konstrukcja przestrzenna. |

Oceniamy sylwetkę całej sukienki. Dopasowana góra i rozkloszowany dół oznaczają `A-Line`. Samo drapowanie, asymetria, plisy ani słowo `relaxed` nie przesądzają o sylwetce. Brak możliwości rozpoznania nie oznacza `Other`.

## Typ (`dress_type`, multichoice)

| Wartość | Znaczenie i wskazówki |
| :--- | :--- |
| `Slip` | Sukienka bieliźniana typu slip; same cienkie ramiączka lub satyna nie wystarczają. |
| `Shirt Dress` | Konstrukcja koszulowa lub polo (`shirt dress`, `shirtdress`, `shirt-style`, `polo dress`). |
| `Wrap` | Konstrukcja kopertowa (`wrap dress`, `surplice`); samo drapowanie lub pasek nie wystarczają. |
| `Sweater Dress` | Konstrukcja swetra (`sweater dress`, `jumper dress`); samo słowo `knit` nie wystarcza. |
| `Sweatshirt Dress` | Konstrukcja bluzy, również z kapturem (`sweatshirt dress`, `hoodie dress`). |
| `T-Shirt Dress` | Konstrukcja T-shirtu (`t-shirt dress`, `tee dress`). |
| `Blazer Dress` | Konstrukcja marynarki (`blazer dress`, `blazer-style dress`). |
| `Other` | Sukienka nie ma żadnego z nazwanych typów; wartość występuje samodzielnie. |

Wybieramy wszystkie potwierdzone typy, np. `["Shirt Dress", "Wrap"]`. Lista jest niepusta i nie zawiera powtórzeń. Niepewność rozpoznania nie oznacza `Other`.

## Dekolt (`neckline`, single choice)

| Wartość | Znaczenie |
| :--- | :--- |
| `Crewneck` | Okrągły, blisko szyi. |
| `Scoop Neck` | Głębszy, otwarty dekolt zaokrąglony. |
| `V-Neck` | W serek, również głęboki lub kopertowy. |
| `High Neck` | Golf, półgolf, wysoki komin (`turtleneck`, `roll neck`, `mock neck`, `high neck`, `funnel neck`). |
| `Collared` | Wykładany kołnierzyk lub klapy. |
| `Other` | Pozostałe rozpoznane kształty dekoltu, w tym łódka, kwadratowy, sweetheart, cowl, prosty i asymetryczny. |

Oceniamy rzeczywisty zewnętrzny dekolt. Kontur w serce pod siateczkowym karczkiem nie wymusza `Sweetheart`. Samo wiązanie, wycięcie typu keyhole ani nazwa konstrukcji ramion nie określają kształtu dekoltu. `Off-Shoulder`, `One-Shoulder`, `Halter` i `Strapless` opisuje `strap_style`.

## Konstrukcja góry (`strap_style`, single choice)

| Wartość | Znaczenie |
| :--- | :--- |
| `Standard` | Zwykłe ramiączka, bez specjalnego układu. |
| `Racerback` | Ramiączka schodzące się na plecach w układ T lub Y. |
| `Halter` | Ramiączko lub materiał biegnący wokół szyi. |
| `One-Shoulder` | Konstrukcja na jedno ramię, również z jednym rękawem. |
| `Strapless` | Góra bez ramiączek i rękawów podtrzymujących konstrukcję. |
| `Off-Shoulder` | Konstrukcja opuszczona poniżej ramion, również z rękawami. |
| `Other` | Rozpoznana konstrukcja spoza powyższych wartości, w tym zwykła konstrukcja z rękawami. |

Przy konstrukcjach mieszanych pierwszeństwo: `One-Shoulder`, następnie `Off-Shoulder`, `Halter`, `Racerback`, `Standard`. `Strapless` stosujemy wyłącznie po potwierdzeniu jego definicji, a `Other` po potwierdzeniu konstrukcji spoza nazwanych klas.

## Szerokość ramiączek (`strap_width`, single choice)

- `Wide`: szerokie ramiączka.
- `Spaghetti`: cienkie ramiączka.
- `Other`: ramiączka pośredniej szerokości lub ramiączka o różnych szerokościach.
- `Not Applicable`: produkt nie ma rzeczywistych ramiączek.

`Strapless` wymaga `strap_width = Not Applicable`. Przy `strap_style = Other` szerokość określamy według rzeczywistej konstrukcji; brak ramiączek oznacza `Not Applicable`. Przy `One-Shoulder`, `Off-Shoulder` i `Halter` oceniamy rzeczywistą konstrukcję: szerokość przypisujemy tylko obecnym ramiączkom, nigdy rękawowi lub zabudowanemu panelowi przy szyi. Nieustalona szerokość istniejących ramiączek oznacza wykluczenie produktu, nie `Not Applicable`.

## Pozostałe cechy i walidacja

- `gender`: single choice, ścisłe mapowanie pola źródłowego do `Men` lub `Women`.
- `colors`: 1–2 różne kolory bazowe albo samo `Multicolor`. Obowiązuje słownik i mapowanie odcieni z `colors_mapping.md`; nie rozróżniamy koloru dominującego.
- `main_composition`: jeden wiarygodnie ustalony skład głównej części, suma 100%. Stosujemy słownik materiałów z `materials_mapping.md`, sumując udziały surowców mapowanych do tego samego enuma. Nie dodajemy składu podszewki, paneli ani zdobień do składu głównego. Nie wybieramy automatycznie pierwszej części. Nie zgadujemy procentów, nie normalizujemy błędnych sum i nie uśredniamy składów różnych części bez ich udziałów. Nierozstrzygalny skład oznacza wykluczenie produktu.
- `pattern`: lista bez powtórzeń. `Solid` i `Other` samodzielnie; konkretne wzory można łączyć. Jeśli występuje nazwany wzór, nie dodajemy do niego `Other` za logo czy grafikę. `Other` stosujemy przy rozpoznanym wzorze bez dopasowania do nazwanych klas. `Solid` wymaga potwierdzenia gładkiego produktu, a nie tylko braku informacji.
- `length`: single choice: `Mini`, `Midi`, `Maxi`. `MID LENGTH DRESSES` odpowiada grupie midi. Przy nierozstrzygalnej długości, również asymetrycznej, wykluczamy produkt.
- `sleeve_length`: single choice: `Sleeveless`, `Short Sleeve`, `Three-Quarter Sleeve`, `Long Sleeve`. Rękaw 3/4 kończy się na przedramieniu, między łokciem a nadgarstkiem. Rękaw dokładnie do łokcia i nieustalona długość są poza docelowym indeksem.
- Nie stosujemy `null`, pustych list ani niewybranych wartości. `Other` i `Not Applicable` nie zastępują niepewności ekstrakcji. Reguły dotyczą produktu; brak wymagania w zapytaniu oznacza pominięcie filtra.
- `fit`, `dress_style`, `shoulder_style` i `full_composition_text` nie należą do schematu `Dresses`.
