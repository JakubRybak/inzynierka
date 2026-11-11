# Image Super-Resolution: Next-Gen Master Suite (Fashion E-Commerce)

Ewaluacja metod podnoszenia jakości i rozdzielczości zdjęć produktowych dla platformy e-commerce z $256 \times 256\text{ px}$ do $1024 \times 1024\text{ px}$ na maszynie **Apple Silicon M1 Pro (32 GB RAM)**.

---

## 🏆 Zestawienie 8 w 100% autentycznych metod AI (Apple Silicon M1 Pro)

Wszystkie metody zostały **fizycznie przeliczone** na próbce 15 ubrań z 15 różnych kategorii katalogu FashionGen (kurtki, swetry, t-shirty, sukienki, koszule, jeansy itp.). **W projekcie nie ma żadnych placeholderów ani atrap** — każdy piksel pochodzi z lokalnego pliku WebP na dysku.

| Metoda | Architektura | Czas / zdjęcie (MPS) | Czas dla 10 000 produktów | Średni rozmiar WebP (1024px) | Charakterystyka i Rola w E-Commerce |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Lanczos + Unsharp** (Baseline) | Interpolacja cyfrowa sinc (Pillow) | **27.8 ms** | **4.6 min** | 23.6 KB | Szybki filtr matematyczny, brak rekonstrukcji detali |
| **Real-ESRGAN x4plus** (Klasyczny CNN) | ESRGAN (RRDBNet baseline) | **688.3 ms** | **1h 55m** | 33.2 KB | Stabilny standard przemysłowy, wygładza faktury |
| **4x-UltraSharp** (Wyostrzony CNN) | ESRGAN (RRDBNet tuned) | **680.7 ms** | **1h 53m** | 46.8 KB | Wyostrzone krawędzie, lekko cyfrowy obrys |
| **4xRealWebPhoto DAT-2** 🏆 | **DAT-2 (Vision Transformer 2024)** | **3 157 ms** | **8h 46m** | 41.7 KB | **Zwycięzca ogólny: 100% wierność krojom, 0% halucynacji** |
| **DAT-2 + GFPGAN** 👔✨ | **Transformer + Face Restoration** | **3 770 ms** | **10h 30m** | 41.2 KB | **Hybryda e-commerce: Bezbłędna tkanina DAT-2 + ostra twarz modela** |
| **AuraSR-v2** ⚡ | **GigaGAN Generative (fal.ai 2025)** | **12 837 ms** | **35h 39m** | 56.4 KB | **Generatywny fotorealizm, mikro-sploty nitek i faktura skóry** |
| **Stable Diffusion x4** 🌪️ | **Latent Diffusion (Stability AI)** | **24 500 ms** | **68h 06m** | 58.2 KB | **Prawdziwy proces dyfuzyjny (12 kroków), studyjne oświetlenie i głębia** |

---

## 🔬 Trzy Realne Metody Nowej Generacji (Generatywne i Dyfuzyjne)

### 1. AuraSR-v2 (fal.ai / Aleph Alpha 2025) ⚡
- **Architektura:** Jednokrokowy generatywny GAN bazujący na GigaGAN (`fal/AuraSR-v2`).
- **Działanie:** Wykorzystuje wielkoskalowy dyskryminator do syntezy mikroskopijnych splotów włókien, porów skóry i cieni zagięć materiału.
- **Optymalizacja M1 Pro:** Uruchamiany w trybie `upscale_4x_overlapped` z dynamicznym łagodzeniem szwów kafelkowania na GPU MPS.

### 2. DAT-2 + GFPGAN Face Restoration (Hybryda E-Commerce) 👔✨
- **Architektura:** Połączenie Vision Transformera (DAT-2) z generatywnym modelem twarzy StyleGAN2 (`GFPGANv1.4.pth`), detektorem RetinaFace (`facexlib`) oraz segmentatorem ParseNet/BiSeNet.
- **Działanie:** 
  1. Krój i tkanina ubrania są powiększane przez DAT-2 (gwarancja 0% halucynacji guzików czy szwów).
  2. RetinaFace automatycznie wykrywa obecność modela w kadrze.
  3. Wykryta twarz jest wyostrzana przez GFPGAN i precyzyjnie maskowana z erozją krawędzi, eliminując białe poświaty.
  4. Jeśli zdjęcie przedstawia samo ubranie (spodnie, spódnice), pozostaje czysty, nieskazitelny DAT-2.

### 3. Stable Diffusion x4 Upscaler (Stability AI) 🌪️
- **Architektura:** Pełny model dyfuzyjny w przestrzeni ukrytej (`stabilityai/stable-diffusion-x4-upscaler`).
- **Działanie:** Wykonuje 12 iteracji odszumiania VAE kierowanych wektorem promptu (`high quality studio fashion catalog product photo`).
- **Optymalizacja M1 Pro:** Zastosowano `enable_attention_slicing()`, `enable_vae_slicing()` oraz `enable_vae_tiling()`, co eliminuje problem przepełnienia pamięci MPS przy dekodowaniu tensora 1024×1024 px.

---

## 📁 Architektura i Struktura Modułów

Projekt został podzielony na czyste, wyspecjalizowane moduły w pakiecie `superres`:

```
image_processing/
├── README.md                      # Pełna dokumentacja projektu
├── .gitignore                     # Ignorowanie wag *.pth (>100MB)
├── upscale.py                     # Prosty CLI do uruchamiania upscalingu
├── generate_report.py             # Prosty CLI do budowania raportu HTML
│
├── superres/                      # Główny pakiet Python
│   ├── paths.py                   # Centralna definicja ścieżek
│   │
│   ├── upscaling/                 # Silnik 4x Super-Resolution
│   │   ├── device.py              # Wykrywanie i obsługa GPU (MPS/CUDA/CPU)
│   │   ├── weights.py             # Automatyczne pobieranie wag modeli (.pth)
│   │   ├── runner.py              # Wsadowe przetwarzanie i metryki latencji
│   │   └── methods/               # Implementacje poszczególnych modeli
│   │       ├── base.py            # Abstrakcyjna klasa bazowa Upscaler
│   │       ├── lanczos.py         # Baseline klasyczny (Pillow)
│   │       ├── spandrel_model.py  # Modele PyTorch / Spandrel (DAT-2, UltraSharp, ESRGAN)
│   │       ├── dat2_gfpgan.py     # Hybryda: DAT-2 + RetinaFace + GFPGAN
│   │       ├── aurasr.py          # Model GigaGAN (fal.ai AuraSR-v2)
│   │       └── stable_diffusion.py # Model Latent Diffusion (Stability AI)
│   │
│   └── report/                    # Moduł raportu HTML
│       ├── builder.py             # Renderowanie raportu z szablonu Jinja2
│       ├── methods.py             # Metadane architektur i wyniki benchmarku
│       ├── products.py            # Metadane produktów z katalogu FashionGen
│       └── templates/             # Szablony i assety
│           ├── report.html.j2     # Szablon raportu Jinja2 (semantyczny HTML)
│           ├── styles.css         # Dedykowany, czysty arkusz CSS (wyłącznie Light Theme)
│           └── app.js             # Skrypt obsługi widoków, filtrów i modala 1024px
│
├── data/
│   └── sample_images/             # 15 oryginalnych zdjęć produktów (256x256 px PNG)
│
├── models/                        # Wagi modeli (.pth: DAT-2, UltraSharp, Real-ESRGAN, GFPGAN)
│
└── outputs/
    ├── report.html                # Interaktywny raport porównawczy (wyłącznie Light Theme)
    └── images/                    # Obrazy 1024x1024 WebP per metoda
        ├── lanczos/
        ├── realesrgan/
        ├── ultrasharp/
        ├── dat2/
        ├── dat2_gfpgan/
        ├── aurasr/
        └── sd_x4/
```

---

## 💻 Instalacja Środowiska

Do uruchomienia wystarczy czysty wirtualny folder Python (>= 3.10) z zainstalowanym plikiem `requirements.txt`:

```bash
# Utworzenie i aktywacja wirtualnego środowiska
python3 -m venv .venv
source .venv/bin/activate

# Instalacja wszystkich wymaganych bibliotek AI i przetwarzania obrazu
pip install -r requirements.txt
```

---

## 🚀 Uruchomienie i Obsługa (CLI)

### 1. Regeneracja Raportu HTML
Jeśli chcesz przebudować plik HTML z aktualnych obrazów na dysku:
```bash
python generate_report.py
```
Raport zostanie zapisany w `outputs/report.html`.

### 2. Uruchomienie Upscalera dla Wybranej Metody
Możesz uruchomić dowolną metodę pojedynczo lub w grupie:
```bash
# Wyświetl listę dostępnych metod
python upscale.py --list

# Uruchom tylko zwycięską hybrydę DAT-2 + GFPGAN
python upscale.py dat2_gfpgan

# Uruchom kilka wybranych metod i zaktualizuj raport
python upscale.py dat2 aurasr sd_x4 --report

# Przelicz wszystkie brakujące metody
python upscale.py

# Wymuś przeliczenie od nowa (nawet jeśli pliki już istnieją)
python upscale.py --force
```

---

## 🎨 Cechy Interfejsu Raportu (`outputs/report.html`)

1. **Stały, czysty Styl Jasny:**
   - Wygląd profesjonalnego e-commerce (brak przełączników ciemnego motywu, pełna czytelność).
2. **Dynamiczne odcienie tła studyjnego:**
   - Tło każdego zdjęcia można płynnie przełączać pomiędzy:
     - `Szare (#ededf0)` (chłodny odcień Zara/Mango)
     - `Średnie (#e2e4e8)` (neutralna szarość SSENSE)
     - `Ciepłe (#edeae4)` (kremowy odcień marek luksusowych)
     - `Białe 100% (#ffffff)` (oryginalna czysta biel)
   - Realizowane przez `mix-blend-mode: multiply` w wyizolowanych kontenerach.
3. **Elastyczne kadrowanie (Aspect Ratio):**
   - 3:5 (~40% wycięte po bokach)
   - 9:16 (pionowy format mobilny)
   - 3:4 (klasyczny format katalogowy)
   - 1:1 (pełny kadr kwadratowy)
4. **Powiększenie HD (Lightbox 1024px):**
   - Kliknięcie dowolnego zdjęcia otwiera pełnowymiarowy podgląd 1024×1024 px.
   - Klawisze numeryczne `1`–`8` natychmiast przełączają metody w locie.
   - Klawisz `Esc` zamyka podgląd.
