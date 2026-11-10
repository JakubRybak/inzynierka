# Image Super-Resolution Benchmark (Fashion E-Commerce)

Ewaluacja metod podnoszenia jakości i rozdzielczości zdjęć produktowych dla platformy e-commerce z $256 \times 256\text{ px}$ do $1024 \times 1024\text{ px}$ na maszynie **Apple Silicon M1 Pro (32 GB RAM)**.

---

## 🚀 Wyniki benchmarku na Apple Silicon M1 Pro (MPS)

Testy przeprowadzono na próbie **15 ubrań** z 15 różnych kategorii katalogu (kurtki, swetry, t-shirty, sukienki, koszule, jeansy itp.).

| Metoda | Architektura | Średni czas / zdjęcie | Przepustowość | **Szacowany czas dla 10 000 produktów** | Średni rozmiar WebP (1024px) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Lanczos + Unsharp** (Baseline klasyczny) | Interpolacja cyfrowa (Pillow) | **27.8 ms** | 36.0 fps | **4.6 min** (0.08 h) | 23.6 KB |
| **4x-UltraSharp** 🏆 *(Rekomendowana szybkość)* | ESRGAN (RRDBNet tuned) | **680.7 ms** | 1.47 fps | **1h 53m** (1.89 h) | 46.8 KB |
| **Real-ESRGAN x4plus** | ESRGAN (RRDBNet baseline) | **688.3 ms** | 1.45 fps | **1h 55m** (1.91 h) | 33.2 KB |
| **4xRealWebPhoto** 🏆 *(Rekomendowana jakość)* | **DAT-2** (Dual Aggregation Transformer) | **3 157.0 ms** | 0.32 fps | **8h 46m** (8.77 h) | 41.7 KB |

---

## 📁 Struktura katalogu

```
image_processing/
├── README.md                  # Niniejszy opis
├── .gitignore                 # Ignorowanie plików wag *.pth (>100MB)
├── benchmark.py               # Główny skrypt benchmarkujący z synchronizacją GPU MPS
├── sample_images/             # 15 przykładowych zdjęć produktów z bazy (256x256)
├── models/                    # Pobrane wagi modeli (.pth)
└── outputs/                   # Przeskalowane obrazy i raporty
    ├── bicubic/               # Wyniki interpolacji Lanczos
    ├── realesrgan_x4plus/     # Wyniki modelu Real-ESRGAN x4plus
    ├── ultrasharp_x4/         # Wyniki modelu 4x-UltraSharp
    ├── realwebphoto_dat2/     # Wyniki modelu 4xRealWebPhoto DAT-2
    ├── comparison_report.html # Interaktywny raport HTML z podglądem wszystkich zdjęć
    ├── benchmark_results.json # Surowe metryki JSON
    ├── montage_*.jpg          # Zestawienia porównawcze całych sylwetek
    └── crop_*.jpg             # Zestawienia powiększeń mikro-detali tkanin
```

---

## 🛠️ Uruchomienie

1. Uruchomienie benchmarku na próbkach:
```bash
.venv/bin/python image_processing/benchmark.py
```

2. Ponowne wygenerowanie samego raportu HTML (bez ponownego przeliczania sieci):
```bash
.venv/bin/python image_processing/benchmark.py --report-only
```

3. Podgląd wizualny:
Otwórz plik `image_processing/outputs/comparison_report.html` w przeglądarce.
