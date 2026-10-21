# Review taksonomii — decyzje i najważniejsze wnioski

Przejrzano **18 kategorii, 44 645 unikalnych produktów, 165 zestawów cech i 1025 wartości w ich kontekście kategorii**. Zakres obejmuje train i validation, bez Jackets & Coats. To przegląd; propozycje poniżej nie zostały wpisane do taksonomii.

- [Wszystkie tabele częstości](taxonomy_keyword_audit.md) — liczby, procenty, keywordy, pokrycie cech i dodatkowe sygnały.
- [Ocena z perspektywy klienta](taxonomy_customer_review.md) — wszystkie kategorie, niejednoznaczności, brakujące możliwości wyszukiwania oraz miejsca do poprawienia w dokumentacji.

## Moja ocena

Rdzeń taksonomii jest dobrze uporządkowany. Przed uznaniem tej części projektu za zamkniętą poprawiłbym przede wszystkim **znaczenie mapowania materiałów** oraz **tłumaczenie potocznych kategorii użytkownika na kategorie źródłowe**. Zmniejszanie liczby rzadkich dekoltów jest kolejną decyzją, ale nie zastąpi tych dwóch poprawek.

## 1. Pierwsze wartości do rozważenia przy upraszczaniu

W kolumnie wynik jest procent produktów z trafieniem szerokiego keywordu, nie udział zweryfikowanych etykiet. Przy Dresses dekolty mają około 88% pokrycia tekstowego; w Sweatshirts około 98%. Nawet przy takim pokryciu poszczególne kształty mogą być nierówno opisywane.

| Kategoria | Cecha | Wartość | Trafienia / produkty (%) | Moja propozycja |
| :--- | :--- | :--- | ---: | :--- |
| Dresses | `neckline` | `Straight Neck` | 3 / 2600 (0,12%) | Pierwszy kandydat do Other. Jawna nazwa ma znikome pokrycie; to nie dowód braku prostych dekoltów. |
| Dresses | `neckline` | `Asymmetric` | 1 / 2600 (0,04%) | Pierwszy kandydat do Other; konstrukcję na jedno ramię nadal opisuje One-Shoulder. |
| Dresses | `neckline` | `Cowl Neck` | 16 / 2600 (0,62%) | Rozważyłbym Other, zgodnie z uproszczeniem przyjętym już dla Tops i Sweaters. |
| Dresses | `neckline` | `Sweetheart` | 14 / 2600 (0,54%) | Kandydat do dyskusji; ma odrębne znaczenie, więc niski procent sam nie przesądza o usunięciu. |
| Dresses | `neckline` | `Square Neck` | 22 / 2600 (0,85%) | Kandydat do dyskusji; zachowanie tej czytelnej klasy też jest rozsądne. |
| Dresses | `dress_type` | `Blazer Dress` | 14 / 2600 (0,54%) | Przy preferencji krótszej listy przeniósłbym do Other. |
| Sweatshirts | `neckline` | `Scoop Neck` | 3 / 3432 (0,09%) | Przeniósłbym do Other przy upraszczaniu tej kategorii. |
| Sweatshirts | `neckline` | `Collared` | 8 / 3432 (0,23%) | Przeniósłbym do Other przy upraszczaniu tej kategorii. |
| Sweatshirts | `neckline` | `V-Neck` | 9 / 3432 (0,26%) | Również kandydat do Other; decyzja oznacza utratę twardego filtra na te bluzy. |
| Knit Sweaters | `neckline` | `Scoop Neck` | 25 / 4990 (0,50%) | Można przenieść do Other; pozostawienie wspólnego słownika Sweaters także ma wartość. |
| Cardigans | `neckline` | `Scoop Neck` | 0 / 904 (0,00%) | Brak trafień; dobry kandydat do usunięcia jako osobnej wartości, jeśli upraszczamy dekolty swetrów. |

**Najprostszy pierwszy krok:** dodać `Other` do `Dresses.neckline` i rozważyć przeniesienie tam `Straight Neck`, `Asymmetric`, `Cowl Neck`. `Square Neck` i `Sweetheart` zostawiłbym do osobnej decyzji: są rzadko nazwane, lecz czytelne dla klienta. Dla Sweatshirts można zejść do `Crewneck / High Neck / Other`, jeśli świadomie akceptujemy brak twardego filtrowania trzech rzadziej opisywanych dekoltów.

Nie stosowałbym automatycznej reguły „poniżej 1% → usuń” dla wszystkich cech. Oznaczałaby także usunięcie standardowych wartości, które niemal nigdy nie są nazywane w opisach.

## 2. Co zachowałbym mimo małej liczby trafień

| Obszar | Powód |
| :--- | :--- |
| `Regular`, `Full-Length`, `Without Hood`, `Solid`, `Standard`, `Open Hem` | Wiele opisów pomija zwykłe cechy. Zero trafień słowa nie oznacza zera produktów. |
| `strap_width` | W opisach rzadko pada dosłownie „wide/thin straps”. Sam ten audyt nie daje podstaw do usunięcia szerokości ramiączek. |
| Wspólne kolory i materiały | Jednolity słownik jest użyteczny nawet przy rzadkim kolorze lub surowcu w małej kategorii. Ponadto badanie nie obejmuje Jackets & Coats. |
| `Mid-Rise` | To potrzebne dopełnienie niskiego i wysokiego stanu; zachowałbym wcześniejszą decyzję. |
| `fit` i `leg_shape` | Odpowiadają na różne pytania. Małe pokrycie słów w tekście nie jest argumentem za połączeniem pól. |
| Zapięcia w Sweaters | Część wartości jest rzadka w jednym podtypie, ale przydatna w innych. Nie tworzyłbym teraz wielu odrębnych słowników zapięć. |

W `T-shirts` istniejący uproszczony dekolt zostawiłbym: Crewneck 91,20%, Scoop Neck 2,41%, V-Neck 1,57%, High Neck 1,66%. Wszystkie nazwane kształty mają widoczny sygnał w danych.

## 3. Materiały wymagają naprawy znaczenia

Szeroki słownik bazujący na obecnym mappingu daje inne wyniki niż same konkretne nazwy i bliskie synonimy. Obie metody liczą całe `input_composition`, w tym podszewki i detale; nie są ekstrakcją głównej części.

| Wartość | Szeroki obecny słownik | Konkretna nazwa / bliskie synonimy | Dodatkowe trafienia szerokiego słownika |
| :--- | ---: | ---: | ---: |
| Polyester | 9178 | 7893 | 1285 |
| Viscose | 7180 | 5352 | 1828 |
| Linen | 1048 | 978 | 70 |

To różnica liczby trafień dwóch słowników, a nie liczba produktów z potwierdzonym błędem składu głównego. Pokazuje jednak, że decyzja o synonimach ma praktyczny wpływ na wiele rekordów. Konkretne błędne scalenia i źródło terminologii są opisane w przeglądzie klienta. Zachowałbym prawdziwy skład; nie zamieniałbym brakującego surowca na podobny tylko po to, żeby zmieścić się w enumach.

## 4. Kategorie źródłowe wymagają szerszej interpretacji zapytań

| Kategoria | Men | Women |
| :--- | ---: | ---: |
| Sweatpants | 1431 | 0 |
| Lounge Pants | 0 | 705 |
| Cargo Pants | 188 | 0 |

Zachowanie źródłowych kategorii jest możliwe, ale „damskie spodnie dresowe” nie może oznaczać wyłącznie `category = Sweatpants AND gender = Women`. Nazwy potrzeb użytkownika trzeba mapować na zakres kategorii. Podobnie „bluza z kapturem” może wymagać przeszukania również Sweatshirts z `hood = With Hood`.

## 5. Braki, które warto świadomie rozstrzygnąć

| Temat | Co znalazłem | Rekomendacja |
| :--- | :--- | :--- |
| `Dresses.neckline` bez `Other` | Nie ma miejsca na rozpoznany kształt poza 11 nazwami. | Dodać Other przed upraszczaniem listy. |
| Rękaw do łokcia | Mapping wyklucza go ze wszystkich kategorii z długością rękawa. | Domknąć granicę: Short Sleeve do łokcia włącznie, Three-Quarter Sleeve poniżej łokcia do przedramienia. To propozycja definicji, nie nowy enum. |
| Zwykłe ramiączka | Między bardzo cienkimi Spaghetti a szerokimi Wide brakuje jasnej granicy. | Ustalić, że Wide obejmuje zwykłe i szerokie ramiączka taśmowe. |
| Grafika / logo | Wzmianki w 52,10% T-shirts i 54,46% Sweatshirts; część to małe logo i detale. Wszystko trafia do szerokiego Other albo jest pomijane przy nazwanym wzorze. | To sensowny kandydat na jedno szerokie Graphic, jeśli chcemy twardo wyszukiwać koszulki z grafiką. Rozstrzygnąć znaczenie małego logo; nie utożsamiać samego słowa logo z dużą grafiką. |
| Tkanina / wykonanie | Denim pojawia się m.in. w 6,11% Shirts i 11,81% Skirts. Koronka i satyna też występują poza składem surowcowym. | To realnie brakująca oś. Świadomie zostawić ją rankingowi albo dodać osobną cechę; nie wkładać Denim/Satin/Lace do main_composition. Ranking nie gwarantuje twardego spełnienia takiego wymagania. |
| Długość polo | 8 z 590 opisów/nazw ma crop/cropped/longline (1,36%). | Przy priorytecie prostoty nie traktowałbym dodania length jako pilnego; można zachować świadomy brak filtra. |

Rękaw 3/4 w Tops: jawne wzmianki dotyczą 55 T-shirts (0,61%), jednego polo (0,17%) i jednego body (0,85%). Zgodnie z Twoją gotowością do odrzucania niszy można pozostawić obecny zakres; to zgrubny sygnał straty, a nie pełne zliczenie produktów wymagających wykluczenia.

## 6. Wiarygodność i odtworzenie

Zliczanie deduplikuje po `input_productID`, używa pełnej liczebności kategorii jako mianownika i niezależnie liczy każdą wartość. Sprawdzono kompletność wszystkich 1025 kombinacji, zgodność sum kategorii, poprawność procentów i przykładowe trafienia. Słownik obejmuje m.in. warianty separatorów, literówki materiałów, elasticised/elasticized i Y-neck jako szeroki sygnał V-Neck.

Dla części wartości użyto jawnie oznaczonych przybliżeń: szlufki/rozporek jako sygnały Structured, french terry/fleece jako sygnały Sweatshorts, rękawy jako sygnał braku ramiączek. Wyniki mogą nakładać się zgodnie z założeniem audytu. Braku trafień nie uzupełniano wartością domyślną.

Raport procentowy można odtworzyć skryptem [audit_taxonomy_keywords.py](../scripts/audit_taxonomy_keywords.py); [JSON](taxonomy_keyword_audit.json) zachowuje regexy, liczniki i przykładowe ID. Główny dokument taksonomii i istniejące mappingi nie zostały zmienione.
