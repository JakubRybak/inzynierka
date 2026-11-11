# Image Super-Resolution: Next-Gen Master Suite (Fashion E-Commerce)

Ewaluacja metod podnoszenia jakości i rozdzielczości zdjęć produktowych dla platformy e-commerce z $256 \times 256\text{ px}$ do $1024 \times 1024\text{ px}$ na maszynie **Apple Silicon M1 Pro (32 GB RAM)**.

---

## Czasy przetwarzania na Apple M1 Pro

Porównanie obejmuje 15 zdjęć FashionGen. Czas na zdjęcie obejmuje wykonanie metody powiększania. Czas dla 10 000 zdjęć jest szacunkiem na podstawie tej wartości.

| Metoda | Architektura | Czas na zdjęcie | Szacunek dla 10 000 zdjęć |
| --- | --- | ---: | ---: |
| **Lanczos + Unsharp** (Baseline) | Interpolacja cyfrowa sinc (Pillow) | **27.8 ms** | **4.6 min** |
| **Real-ESRGAN x4plus** (Klasyczny CNN) | ESRGAN (RRDBNet baseline) | **688.3 ms** | **1h 55m** |
| **4x-UltraSharp** (Wyostrzony CNN) | ESRGAN (RRDBNet tuned) | **680.7 ms** | **1h 53m** |
| **4xRealWebPhoto DAT-2** | **DAT-2 (Vision Transformer 2024)** | **3 157 ms** | **8h 46m** |
| **DAT-2 + GFPGAN** | **Transformer + Face Restoration** | **3 770 ms** | **10h 30m** |
| **AuraSR-v2** | **GigaGAN Generative (fal.ai 2025)** | **12 837 ms** | **35h 39m** |
| **Stable Diffusion x4** | **Latent Diffusion (Stability AI)** | **24 500 ms** | **68h 06m** |

## Metody

- **AuraSR-v2** używa modelu opartego na GigaGAN i powiększa obraz w nakładających się kafelkach.
- **DAT-2 + GFPGAN** powiększa zdjęcie za pomocą DAT-2, wykrywa twarze za pomocą RetinaFace i nakłada fragmenty przetworzone przez GFPGAN z maską z ParseNet.
- **Stable Diffusion x4** wykonuje 12 kroków odszumiania z instrukcją tekstową. Pipeline używa dzielenia obliczeń uwagi oraz dzielenia i kafelkowania VAE.

---

## 📁 Architektura i Struktura Modułów

Projekt został podzielony na czyste, wyspecjalizowane moduły w pakiecie `superres`:

```
image_processing_experiments/
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
│           └── app.js             # Obsługa widoku, tła i kadru
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

# Uruchom tylko hybrydę DAT-2 + GFPGAN
python upscale.py dat2_gfpgan

# Uruchom kilka wybranych metod i zaktualizuj raport
python upscale.py dat2 aurasr sd_x4 --report

# Przelicz wszystkie brakujące metody
python upscale.py

# Wymuś przeliczenie od nowa (nawet jeśli pliki już istnieją)
python upscale.py --force
```

---

## Widoki raportu

- **Porównanie produktu** pokazuje oryginał i wszystkie warianty każdego zdjęcia obok siebie.
- **Storefront** grupuje zdjęcia według metody powiększania.
- Ustawienia tła, kadru i liczby kolumn działają w obu widokach.
