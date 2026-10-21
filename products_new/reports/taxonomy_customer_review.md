# Przegląd taksonomii z perspektywy klienta

Zakres: 18 kategorii w działach Tops, Shirts & Blouses, Sweaters, Pants, Shorts, Skirts i Dresses. Jackets & Coats pozostają poza przeglądem. Stan dokumentacji: 20.10.2026.

Podstawą są [aktualna taksonomia](../../categories_and_features/categories_and_features.md) i pliki mapowania. To ocena znaczenia cech i możliwości wyszukiwania. **Wszystkie przykłady zapytań są hipotetyczne**: nie pochodzą z przeanalizowanych logów Amazon i nie świadczą o popularności danej potrzeby. Częstości słów w produktach są w [raporcie statystycznym](taxonomy_keyword_audit.md); [krótka lista decyzji](taxonomy_review_decisions.md) łączy wnioski z obu części.

**Podział kategorii w większości zostawiłbym. Najważniejsza poprawka dotyczy materiałów: część obecnych mapowań zmienia nazwę rzeczywistego surowca.** Dalej poprawiłbym granice długości rękawów i doprecyzował kilka definicji. Nie rozbudowywałbym automatycznie każdej kategorii o wszystkie cechy dostępne w pozostałych.

Priorytety: **P1** — poprawić przed ekstrakcją docelowego datasetu; **P2** — uzgodnić zakres lub regułę, bez konieczności rozbudowy list wartości; **P3** — opcjonalna funkcjonalność, którą można świadomie pozostawić rankingowi.

## 1. Decyzje o największym znaczeniu

| Priorytet | Obszar | Problem z perspektywy klienta | Hipotetyczne zapytanie | Proponowana decyzja |
| :--- | :--- | :--- | :--- | :--- |
| P1 | `main_composition` | Słownik scala różne surowce pod nazwą jednego konkretnego materiału. Suma 100% pozostaje poprawna arytmetycznie, ale może przestać opisywać rzeczywisty skład. | „100% lniana koszula”, „spodnie bez poliestru” | Usunąć fałszywe synonimy. Przy obecnym zamkniętym słowniku odrzucać składy, których nie da się zapisać zgodnie z prawdą; nie zastępować brakującego materiału podobnym. Ewentualne rozszerzenie słownika powinno wynikać ze skali takiej straty. |
| P1 | `sleeve_length` | Rękaw dokładnie do łokcia jest wykluczany we wszystkich kategoriach mających tę cechę. To luka pomiędzy wartościami, którą można usunąć bez dodawania enuma. | „bluzka z rękawem do łokcia” | Rozszerzyć `Short Sleeve` do łokcia włącznie; `Three-Quarter Sleeve` pozostawić dla przedramienia. Stosować tę samą granicę wszędzie. |
| P2 | `Dresses.neckline` | To jedyny słownik dekoltów bez `Other`. Redukcja dowolnej rzadkiej wartości oznaczałaby obecnie wykluczenie tych sukienek zamiast ich zachowania jako pozostałych. | „prosta czarna sukienka” — bez wymagania co do dekoltu | Dodać `Other` jako miejsce dla rozpoznanych kształtów poza nazwanymi klasami. Konkretne cięcia spośród 11 wartości oprzeć na raporcie częstości, bez automatycznego zrównania wszystkich kategorii. |
| P2 | `strap_width` | `Spaghetti` oznacza cienkie ramiączka, `Wide` szerokie. Nie wiadomo, co zrobić z wyraźnie istniejącymi ramiączkami pośredniej szerokości. | „top na zwykłych, niecienkich ramiączkach” | Zachować dwie klasy obecnych ramiączek, ale doprecyzować, że `Wide` obejmuje zwykłe i szerokie taśmowe ramiączka, a `Spaghetti` bardzo cienkie. Do wyświetlania można użyć „zwykłe / szerokie”. Nie dodawać osobnego `Medium`. |
| P2 | `Polos.length` | Polo jako jedyna zwykła góra w Tops nie ma długości; T-shirts i Tank tops ją mają. Wybór kategorii może więc usunąć możliwość wyrażenia tej samej potrzeby. | „krótkie polo”, „polo crop” | Jeśli zależy nam na twardym filtrowaniu długości polo, dodać istniejący już zestaw `Cropped / Regular / Longline`. To kandydat do sprawdzenia w danych, nie powód do dodania wielu nowych cech. |
| P1 | Kategorie źródłowe a zapytania | Nazwy klas źródłowych nie gwarantują, że wszystkie produkty o poszukiwanej konstrukcji trafią do jednej kategorii. Szczególnie istotna jest różnica Sweatpants/Lounge Pants zależna w tym zbiorze od płci. | „damskie spodnie dresowe”, „bluza z kapturem”, „sweter z golfem” | Zachować uzgodniony podział produktów. Przy ogólnym zapytaniu przeszukiwać kilka odpowiednich kategorii i używać cech, np. `hood = With Hood`; nie wymuszać automatycznie wyłącznie `Hoodies & Zipups`. |
| P2 | Pozostałości w mapowaniach | Niektóre instrukcje nadal proponują domyślną cechę na podstawie braku słowa albo używają niejednakowych definicji. | „jeansy bez przetarć”, „kardigan na guziki” | Ujednolicić instrukcje ekstrakcji przed użyciem ich w promptach. Nie zmienia to list cech; lista konkretnych miejsc znajduje się w sekcji 5. |

### Materiały: problem jest szerszy niż denim

Słusznie nie ma `Denim`, `Satin` ani `Lace` w składzie procentowym. Jednak [materials_mapping.md](../../categories_and_features/materials_mapping.md) wprowadza inne scalenia, których nie traktowałbym jako zwykłych synonimów:

| Obecne mapowanie | Dlaczego wymaga zmiany | Minimalna poprawka |
| :--- | :--- | :--- |
| `polyurethane`, `polyethylene`, `polypropylene`, `pvc` → `Polyester` | Różne tworzywa są zapisywane jako poliester. | Do `Polyester` kierować poliester i jego literówki, nie dowolny syntetyk. |
| `cupro`, `acetate`, `triacetate`, `modal`, `lyocell` → `Viscose` | Oddzielne nazwy włókien stają się procentem wiskozy. | Zachować tylko rzeczywiste synonimy; pozostałe włókna wymagają odrębnej decyzji o pokryciu słownika. |
| `ramie`, `hemp` → `Linen` | Skład konopny lub ramia zostaje przedstawiony jako lniany. | `Linen` obejmuje len / `flax`; nie przypisywać tu innych włókien tylko z powodu podobieństwa. |
| `elastodiene`, `elastomultiester` → `Elastane` | Elastyczność materiału nie oznacza, że jest elastanem. | Nie scalać na podstawie samej funkcji. |
| `faux fur` → `Fur` | Sztuczne futro staje się tym samym materiałem co futro naturalne; określenie nie podaje też włókna imitacji. | Jeśli znany jest skład włóknisty, użyć go. Sama nazwa imitacji nie wystarcza do wpisania procentu `Fur`. |

Odrębność wymienionych włókien potwierdza wykaz nazw w załączniku I do [rozporządzenia 1007/2011](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32011R1007). Źródło służy sprawdzeniu terminologii materiałowej.

Przykład skutku obecnej reguły: `70% cotton, 30% hemp` staje się `Cotton: 70, Linen: 30`. Filtr „zawiera len” zwróci wówczas produkt, którego surowy skład nie deklaruje lnu. Lepszy model językowy nie usunie problemu, jeśli dostanie taką instrukcję.

Nie proponuję usuwać rzadkiego surowca z danej kategorii tylko dlatego, że ma mały udział produktów. Wspólny słownik materiałów ma sens: rzadkość skórzanej spódnicy i rzadkość szczegółowego kształtu dekoltu mają różne znaczenie dla użytkownika.

## 2. Przegląd wszystkich kategorii

Poniższe uwagi zakładają naprawę wspólnych problemów z poprzedniej sekcji.

| Dział / kategoria | Co jest dobrze ustalone | Co zmieniłbym lub doprecyzował | Ocena |
| :--- | :--- | :--- | :--- |
| Tops — T-shirts | Pięć wartości dekoltu, trzy dopasowania i trzy długości dają prosty, użyteczny podział. | Sprawdzić koszt braku `Three-Quarter Sleeve`; jeśli zostaje poza zakresem, to świadoma utrata produktów, a nie problem do rozwiązania przez LLM. | Zostawić rdzeń; decyzja po częstościach. |
| Tops — Polos | Oddzielna kategoria i brak dodatkowego `neckline` pozwalają uniknąć zbędnego powielania kołnierzyka. | Rozważyć `length`; taka sama potrzeba skróconej góry jest już obsługiwana w sąsiednich kategoriach. | Jedna możliwa luka, P2. |
| Tops — Tank tops & Camisoles | Rozdzielenie konstrukcji góry od szerokości ramiączek ma sens. `Strapless` daje jednoznaczny filtr produktu bez ramiączek. | Doprecyzować zwykłe ramiączka w `Wide`. Brak `Other` w konstrukcji można zachować, jeśli świadomie odrzucamy nietypowe konstrukcje. | Zostawić klucze i sześć konstrukcji. |
| Tops — Bodysuits | Długość rękawa, dekolt i konstrukcja góry opisują różne potrzeby. | Nie uzasadniać braku `fit` twierdzeniem, że każde body jest z definicji obcisłe. Można pominąć ten filtr jako uproszczenie, ale nie wolno na tej podstawie generować etykiet dopasowania. | Brak `fit` można utrzymać; poprawić uzasadnienie. |
| Shirts & Blouses — Shirts | `collar_type` jest czytelniejsze niż dokładanie równoległego dekoltu. `Collarless` nie jest tym samym co `Other`. | `Point Collar` obejmuje też spread/cutaway/button-down: traktować to świadomie jako grupę „klasyczny kołnierzyk koszulowy”, nie obiecywać rozróżnienia dokładnego kształtu. | Zestaw zostawić. |
| Shirts & Blouses — Blouses | `neckline` zamiast szczegółowego kołnierza dobrze pasuje do szerszej grupy fasonów. | Ramiączka, wiązania i odkryte ramiona pozostają poza twardym filtrem; nie rozszerzałbym bluzek o cały zestaw z sukienek. | Zostawić uproszczenie. |
| Sweaters — Knit Sweaters | Krój, długość, rękaw, kaptur, zapięcie i uproszczony dekolt pokrywają różne osie. | Przy szczegółowym zapytaniu „golf” `High Neck` obejmuje też półgolf; to świadome poszerzenie. Nie wprowadzałbym ponownie osobnej wartości bez potrzeby. | Zostawić. |
| Sweaters — Sweatshirts | `hood` nadal jest przydatne mimo osobnej kategorii Hoodies & Zipups, skoro zachowujemy źródłowe etykiety. | Nie używać braku słowa „hood” do przypisania `Without Hood`. | Zestaw zostawić; uwaga dotyczy ekstrakcji. |
| Sweaters — Hoodies & Zipups | Kaptur i sposób otwierania przodu rozróżniają główne warianty; `Half-Zip` ma osobne znaczenie. | Brak `neckline` jest rozsądnym ograniczeniem. Nie dokładałbym go dla zgodności liczby pól z innymi swetrami. | Zostawić. |
| Sweaters — Cardigans | `Open Front`, `Button`, `Zip`, `Belted` są użytecznymi rozróżnieniami. | Ujednolicić znaczenie `Button` w dwóch mappingach; zachować wybraną zasadę o głównym zapięciu. | Słownik zostawić; poprawić mapping. |
| Pants — Trousers | Skóra jako materiał zamiast osobnej kategorii jest klarowna. Oddzielne `fit` i `leg_shape` rozwiązują dawną niejednoznaczność. | `Structured` to konstrukcja pasa, nie elegancki styl; tę granicę utrzymać w ekstrakcji i tłumaczeniu zapytań. | Zostawić. |
| Pants — Cargo Pants | Te same cechy dopasowania, nogawki i pasa co w pozostałych spodniach ułatwiają porównania. | Ogólne „cargo” może opisywać konstrukcję także poza źródłową klasą; sama kategoria nie gwarantuje pełnego pokrycia takiego zapytania. | Podział zostawić, świadomie obsłużyć zakres zapytań. |
| Pants — Sweatpants | `cuff_style` i `waistband_type` wnoszą informację niezależną od samej nazwy kategorii. | Nie zakładać automatycznie gumki w pasie i przy kostkach. | Zostawić. |
| Pants — Lounge Pants | Wspólny zestaw cech zapobiega innym definicjom tej samej nogawki w sąsiednich kategoriach. | Granica Lounge Pants/Sweatpants jest źródłowa; zapytania ogólne „luźne spodnie do domu” powinny móc przeszukiwać obie. | Zostawić kategorie; rozszerzać zakres zapytań. |
| Pants — Jeans | `Skinny / Slim / Regular / Relaxed` niezależnie od nogawki oraz trzy stopnie wykończenia są wystarczająco proste. | Uporządkować `distressing`: brak słowa nie dowodzi `Clean`, a odpryski farby i ozdobne naszywki nie muszą oznaczać fizycznego uszkodzenia. | Zestaw zostawić; poprawić mapping. |
| Shorts — Shorts | `shorts_type` multi choice dobrze obsługuje np. szorty jednocześnie denim i cargo. `Tailored` jest oddzielone od pasa. | Nie dodawałbym `leg_shape`: obecny `fit` i długość wystarczają do przyjętego poziomu szczegółowości. | Zostawić. |
| Skirts — Skirts | Sylwetka oddzielona od plisowania/kopertowości/asymetrii jest właściwa; typ może mieć kilka wartości. | Doprecyzować granicę `Fitted`/`Straight`: prosta spódnica może być zarazem dopasowana. Ustalić pierwszeństwo `Fitted` dla wyraźnego przylegania do ciała, `Straight` dla prostego obrysu bez tego efektu. | Zestaw zostawić; dopracować definicję. |
| Dresses — Dresses | Oddzielne sylwetka, typ, dekolt i konstrukcja ramion unikają powrotu do jednej wielkiej listy fasonów. Brak dodatkowego `fit` jest rozsądny. | Dodać `Other` w dekolcie; stosować wspólną granicę `Fitted`/`Straight`; ustalić pierwszeństwo przy jednoczesnym kołnierzu i otwarciu w serek. | Drobne domknięcie semantyki, bez przebudowy. |

### Dwa konkretne przykłady z danych

- **Sweatpants / Lounge Pants:** `Sweatpants` zawiera 1431 produktów z etykietą Men, a `Lounge Pants` 705 z etykietą Women. Zapytanie „damskie spodnie dresowe” kierowane wyłącznie do Sweatpants da pusty wynik. Zachowałbym kategorie źródłowe, ale tę potrzebę klienta tłumaczył na odpowiedni zakres obu kategorii i filtr gender. Samo rozszerzenie zakresu nie gwarantuje, że każdy Lounge Pants ma konstrukcję dresową; szczegóły nadal wymagają dopasowania do opisu.
- **Luźne body:** produkt `651103`, „Taupe & Beige T-Shirt Bodysuit”, ma w opisie `Relaxed-fit silk-blend short sleeve bodysuit` i dopasowany dolny panel. To konkretny kontrprzykład do uzasadnienia, że wszystkie body są z definicji obcisłe. Nadal można świadomie pominąć `fit` w tej kategorii.

## 3. Spójność znaczeń między kategoriami

| Obszar | Ocena | Reguła, którą warto utrzymać lub doprecyzować |
| :--- | :--- | :--- |
| `fit` a `leg_shape` | Dobry podział. | Dopasowanie spodni dotyczy bioder i ud; kształt nogawki jest osobny. `Relaxed + Tapered` jest poprawne. Szeroka prosta nogawka trafia zgodnie z mappingiem do `Wide-Leg`, nie jednocześnie do `Straight`. |
| Sylwetka sukienki i spódnicy | Zestawy zgodne. | `A-Line` ma pierwszeństwo przy dopasowanej górze i rozkloszowanym dole. Dla pozostałych przypadków wyraźne dopasowanie oznacza `Fitted`, a sam prosty kontur nie wystarcza do `Fitted`. |
| `Crewneck` / `Scoop Neck` / `High Neck` | Znaczenia ujednolicone. | Rozróżnienie wysokiego i głębszego okrągłego dekoltu ma sens. Wspólna nazwa musi oznaczać to samo mimo różnej liczby wartości w kategoriach. |
| `Collared` a `V-Neck` | Niewystarczające pierwszeństwo przy single choice. | Produkt może mieć kołnierz i otwarcie przodu w serek. Proponuję `Collared` dla rzeczywistego wykładanego kołnierza; `V-Neck` opisuje serek bez niego. To ogranicza duble bez tworzenia nowej cechy. |
| `strap_style` a `strap_width` | Dobry podział, mało intuicyjna techniczna nazwa pierwszego pola. | `strap_style` w praktyce opisuje „konstrukcję góry / ramion”, również rękaw na jedno ramię. Tak wyjaśniać je użytkownikowi. `Not Applicable` w szerokości nie jest zamiennikiem `Strapless`. |
| `Other` | Przydatne, ale jego zakres zależy od cechy. | W `dress_type`, `skirt_type`, `shorts_type` może oznaczać zwykły produkt bez szczególnego typu. W dekolcie oznacza rozpoznany kształt poza listą. W żadnym wypadku nie dowodzi, że ekstrakcja zna wynik, jeśli widok i opis go nie rozstrzygają. |
| `pattern` multi choice | Sensowne. | Konkretne wzory można łączyć. `Other` samodzielnie jest akceptowalnym uproszczeniem, ale gubi informację o grafice/logo przy paskach. Nie wyciągać z samego `Striped` wniosku „bez nadruku graficznego”. |
| Długości | Różne zestawy według rodzaju ubrania mają sens. | W mappingu góry `Cropped` i `Regular` oba odnoszą się do talii; w spodniach `Cropped` zawiera ankle-length, a `Full-Length` kończy się przy kostce. Potrzebne są referencje graniczne i pierwszeństwo jednoznacznego opisu produktu. To nie wymaga nowych enumów. |
| `gender` | Wystarcza do uzgodnionego zakresu źródłowych kategorii. | Przypisanie dotyczy etykiety sklepowej. Brak płci w zapytaniu nie powinien wymuszać jednej wartości. Nie wnioskować płci z koloru lub fasonu. |
| `colors` | Prostota zgodna z przyjętą decyzją. | `Multicolor` świadomie usuwa informację o poszczególnych kolorach. Wielokolorowa rzecz z czerwienią nie znajdzie się przez samo `colors contains Red`. To ograniczenie zapisu, nie błąd LLM. |

**Single choice nie wymaga, żeby pojęcia nigdy fizycznie nie współistniały. Wymaga jasnej, stabilnej reguły wyboru.** Jest ona już opisana dla `Wide-Leg` względem `Straight` i dla mieszanych konstrukcji ramion. Trzeba ją równie jasno zapisać przy sylwetce i kołnierzu względem serka. Szczegóły te należą do mappingów, bez rozbudowywania krótkiej sekcji „Zasady” w głównym dokumencie.

## 4. Co może być brakującą funkcją, ale nie musi stać się cechą MVP

| Potrzeba klienta | Co umożliwia obecny schemat | Czego nie gwarantuje | Rekomendacja |
| :--- | :--- | :--- | :--- |
| „satynowa sukienka”, „koronkowa bluzka”, „sztruksowe spodnie” | Ranking może korzystać z opisu i wyglądu. | Skład włóknisty nie określa splotu, struktury ani wykończenia. `Silk` nie jest filtrem na satynę. | Najbardziej wyraźna brakująca oś wyszukiwania. Nie mieszać jej z `main_composition`; na obecnym etapie zostawić rankingowi. Gdy ma być twardym wymaganiem, potrzebna będzie osobna cecha tkaniny/wykonania. |
| „T-shirt z grafiką” albo „bez logo” | `Other` obejmuje część takich produktów. | `Other` obejmuje też colorblock, tie-dye i inne motywy; logo przy paskach jest celowo pomijane. | Jeśli logi zapytań potwierdzą istotność, rozważyć jedno szerokie `Graphic` zamiast szeregu niszowych wzorów. Obecnie nie dodawać automatycznie. |
| „spódnica z rozcięciem” albo „sukienka z kieszeniami” | Ranking może wykrywać te detale. | Żadna obecna cecha nie opisuje wprost ich obecności. | Świadomie pozostawić poza filtrami MVP. Nie mnożyć pól tylko dlatego, że można je nazwać. |
| „bawełniana koszulka” vs „100% bawełny” | Procentowy skład zawiera dane potrzebne do rozróżnienia. | Nie ustalono tu, czy ogólne „bawełniana” wymaga większości bawełny, określonego progu czy dowolnej domieszki. | Nie zmieniać cechy. To osobna reguła tłumaczenia zapytania na warunek procentowy; samo `contains Cotton` może nie oddawać intencji. |
| „rękaw 3/4” w T-shirts, Polos lub Bodysuits | Inne działy znają już taką wartość. | Produkt spoza enumów Tops zostanie wykluczony, nawet przy idealnej ekstrakcji. | Zestawić z liczbami w raporcie. Jeżeli strata jest mała, zaakceptować ograniczenie; jeżeli duża, użyć istniejącej wartości, bez nowego nazewnictwa. |
| „spodnie cargo”, niezależnie od źródłowej kategorii | Kategoria Cargo Pants zawiera źródłowe cargo. | Jeżeli produkt z kieszeniami cargo jest źródłowo w Jeans lub Sweatpants, bieżący schemat nie ma wspólnej cechy `cargo` dla wszystkich spodni. | Nie przebudowywać podziału w tym review. Traktować jako realną granicę twardego filtra; sam ranking nie daje gwarancji spełnienia warunku. |

Przy tych przykładach brak cechy jest decyzją o zakresie produktu. **Opis i embedding mogą poprawić kolejność wyników, ale nie zastępują gwarancji twardego filtra.** To istotne przy określaniu, które fragmenty zapytania uznajemy za bezwzględne wymaganie.

## 5. Konkretne miejsca w dokumentacji wymagające uporządkowania

Nie zmieniono żadnego z tych plików w ramach raportu.

| Plik | Obecny zapis / niespójność | Proponowana poprawka |
| :--- | :--- | :--- |
| [materials_mapping.md](../../categories_and_features/materials_mapping.md) | Materiały wymienione w sekcji 1 raportu traktowane jak synonimy. | Poprawić znaczenie mapowań przed ekstrakcją; nie wystarczy poprawność JSON i sumy procentów. |
| [distressing_mapping.md](../../categories_and_features/distressing_mapping.md) | `Clean` zawiera „absence of ... keywords”. | Brak trafienia keywordu traktować jako brak sygnału. `Clean` ustalać na podstawie opisu i zdjęć. |
| [distressing_mapping.md](../../categories_and_features/distressing_mapping.md) | `selvedge` figuruje jako wskazówka `Clean`, a `paint splatter` i `patched` jako `Distressed`. | Nie wyciągać tych wniosków automatycznie. Sprawdzać faktyczny efekt sprania/uszkodzenia; dekoracja nie wystarcza. |
| [closure_type_mapping.md](../../categories_and_features/closure_type_mapping.md) i [sweaters_mapping.md](../../categories_and_features/sweaters_mapping.md) | Wspólny plik rozszerza `Button` na haftki i kołki; plik Sweaters definiuje guziki i napy. | Przyjąć jedno znaczenie dla Sweaters. Proponuję guziki i napy; pozostałe konstrukcje kierować do `Other`, jeśli mają być poza uproszczonym słownikiem. |
| [patterns_mapping.md](../../categories_and_features/patterns_mapping.md) | Wstęp każe pominąć `Other` przy nazwanym wzorze i logo, a punkt „Grafika/logo jako Other” nie podaje tego wyjątku. | Zostawić jedną pełną regułę: grafika jako `Other` wyłącznie przy braku przypisanego nazwanego wzoru. |
| [patterns_mapping.md](../../categories_and_features/patterns_mapping.md) | `herringbone` wpada do `Plaid`; wzory są opisywane jako grupa wszystkich krat, jodełek i rombów. | Nie traktować samego słowa jako dowodu kraty. Przeanalizować widoczny wzór: do `Plaid` rzeczywista krata, do `Solid` jednolita powierzchnia ze strukturą, do `Other` pozostały wyraźny deseń. |
| [fit_mapping.md](../../categories_and_features/fit_mapping.md) | Brak `fit` w Bodysuits uzasadniono tym, że „z definicji są ściśle dopasowane”; `dropped-shoulder` i `dolman` trafiają do `Relaxed`. | Brak pola uzasadnić ograniczeniem zakresu. Detalu ramienia/rękawa nie utożsamiać automatycznie z dopasowaniem całego korpusu. |
| [length_mapping.md](../../categories_and_features/length_mapping.md) | `Full-Length` opisano jako „wartość domyślna dla spodni”. | Usunąć sugestię domyślnej etykiety przy braku informacji. Domyślny fallback w raporcie keywordowym sztucznie zawyżyłby częstość. |
| [rise_mapping.md](../../categories_and_features/rise_mapping.md) | `Mid-Rise` zawiera sformułowanie o wartości domyślnej; `dropped waist` jest wskazówką `Low-Rise`. | „Standardowy” wymaga rozpoznania, nie braku słowa. `dropped waist` oceniać w kontekście faktycznego położenia pasa, a nie samej linii konstrukcyjnej ubrania. |
| [sleeve_length_mapping.md](../../categories_and_features/sleeve_length_mapping.md) | Elbow-length jest poza zakresem; `bishop sleeve` widnieje przy długim rękawie. | Domknąć granicę przy łokciu. Fason rękawa nie powinien samodzielnie przesądzać jego długości. |
| [colors_mapping.md](../../categories_and_features/colors_mapping.md) | Deklaracja, że obecna tablica obsługuje „wszystkie scenariusze” zapytań o kolor. | Usunąć absolutne stwierdzenie: przy `Multicolor` tracimy możliwość filtrowania po składowych kolorach. Zachować samą zaakceptowaną regułę zapisu. |
| Kilka mappingów | Stare numery i nieudokumentowane liczebności: Jeans jako `5.4`, rise jako 6 kategorii mimo listy 7, nagłówek „11 wzorów” mimo 8. | Usunąć niepotrzebne liczby ze słowników; statystyki trzymać w raporcie z zakresem danych i datą. |

Szerokie keywordy z raportu częstości **nie powinny automatycznie stać się regułami produkcyjnej ekstrakcji**. W audycie użytkownik świadomie dopuszcza jednoczesne trafienia i nadmiarowe sygnały. W docelowym rekordzie wymagamy rozstrzygnięcia zgodnego ze znaczeniem cechy.

## 6. Co uznałbym za zamknięte bez kolejnej przebudowy

- Oddzielenie materiałów procentowych od nazw tkanin i efektów powierzchniowych.
- Wspólna paleta kolorów i brak osobnego koloru dominującego, wraz ze świadomą utratą kolorów składowych `Multicolor`.
- `pattern` jako multi choice z samodzielnym `Solid` i `Other`.
- Oddzielne `fit` i `leg_shape` w spodniach.
- Oddzielne sylwetka i typ dla spódnic oraz sukienek; brak dodatkowego `fit` dla sukienek.
- `collar_type` w Shirts, `neckline` w Blouses; różne zakresy dekoltów w różnych działach.
- Brak ramiączek jako `strap_style = Strapless`; `Not Applicable` wyłącznie w szerokości ramiączek.
- Zachowanie Mid-Rise oraz innych zwykłych wartości, których opisy mogą nie wymieniać dosłownie.
- Brak dodatkowego dekoltu w Hoodies & Zipups i brak ramiączek w Sweaters.
- Wspólne cechy spodni, nawet jeżeli część wartości jest rzadka w pojedynczej podkategorii.

Do usuwania wartości wykorzystałbym procent trafień jako wskazówkę, a następnie sprawdził znaczenie wartości i koszt utraty możliwości wyszukiwania. Niskie trafienia przy `Regular`, `Solid`, `Without Hood`, `Open Hem` albo `Not Applicable` mogą odzwierciedlać sposób pisania opisów. Nie są samodzielnym argumentem za usunięciem tych wartości.
