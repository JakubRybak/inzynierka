# Mapowanie stylu ramiączek (`strap_style`)

Dokument definiuje ujednoliconą listę **5 kanonicznych typów ramiączek** używanych w cesze `strap_style` w kategorii `Tank tops & Camisoles` oraz zasady mapowania określeń ze zbioru Fashion-Gen (`input_name`, `input_description` oraz analiza obrazu).

---

## 1. Zakres kategorii posiadających cechę `strap_style`

Cecha `strap_style` jest specyficzna wyłącznie dla kategorii **`Tank tops & Camisoles`** (w dziale `1. Tops`), gdzie wszystkie produkty są bez rękawów, a szerokość i konstrukcja ramiączek stanowi główną cechę odróżniającą klasyczne tank topy od bieliźnianych topów typu camisole, bokserek czy topów halter.

---

## 2. Tabela mapowania 5 wartości `strap_style`

| # | Wartość docelowa (`strap_style`) | Dotychczasowe warianty (z `/`) zastąpione tą wartością | Określenia ze zbioru Fashion-Gen (`input_name` / `input_description`) mapowane do tej wartości |
| :-: | :--- | :--- | :--- |
| 1 | **`Wide Straps`** | `Wide Straps` | Klasyczne, szersze ramiączka typowe dla topów typu tank top oraz bezrękawników (`wide straps`, `tank top`, `sleeveless top`, `muscle tank`, `thick shoulder straps`, wartość domyślna dla klasycznych tank topów) |
| 2 | **`Spaghetti Straps`** | `Thin / Spaghetti Straps` | Bardzo cienkie, delikatne ramiączka typowe dla topów bieliźnianych typu camisole (`spaghetti straps`, `thin straps`, `camisole`, `cami`, `adjustable shoulder straps`, `lingerie straps`, `delicate straps`) |
| 3 | **`Racerback`** | `Halter / Racerback` | Sportowe ramiączka schodzące się na łopatkach w kształt litery T lub Y – bokserka (`racerback`, `racer-back`, `athletic back`, `swimmer back`) |
| 4 | **`Halter`** | `Halter / Racerback` | Ramiączka zawieszane lub wiązane wokół szyi z odkrytymi ramionami i górną częścią pleców (`halter`, `halterneck`, `halter strap`, `self-tie strap at neck`, `neck strap`) |
| 5 | **`Strapless`** | `Strapless / One-Shoulder` | Topy całkowicie bez ramiączek (bandeau / gorsetowe) lub z asymetrycznym pojedynczym ramiączkiem (`strapless`, `bandeau`, `tube top`, `bustier`, `one-shoulder`, `asymmetric single strap`) |
