# Image Super-Resolution: Next-Gen Master Suite (Fashion E-Commerce)

Ewaluacja metod podnoszenia jakości i rozdzielczości zdjęć produktowych dla platformy e-commerce z $256 \times 256\text{ px}$ do $1024 \times 1024\text{ px}$ na maszynie **Apple Silicon M1 Pro (32 GB RAM)**.

---

## 🏆 Zwycięzca benchmarku: 4xRealWebPhoto DAT-2

W bezpośrednim porównaniu na próbce 15 ubrań z 15 różnych kategorii katalogu (kurtki, swetry, t-shirty, sukienki, koszule, jeansy itp.) model **4xRealWebPhoto (DAT-2 – Dual Aggregation Transformer)** zapewnił najwyższą jakość rekonstrukcji faktury ubrań (sploty wełny, szwy, popelina, denim) przy zerowych halucynacjach (0% zniekształceń logotypów i krojów).

| Metoda | Architektura | Czas / zdjęcie (MPS) | Czas dla 10 000 produktów | Średni rozmiar WebP (1024px) |
| :--- | :---: | :---: | :---: | :---: |
| **Lanczos + Unsharp** (Baseline) | Interpolacja cyfrowa (Pillow) | **27.8 ms** | **4.6 min** | 23.6 KB |
| **4x-UltraSharp** (Szybki GAN) | ESRGAN (RRDBNet tuned) | **680.7 ms** | **1h 53m** | 46.8 KB |
| **Real-ESRGAN x4plus** (Klasyczny CNN) | ESRGAN (RRDBNet baseline) | **688.3 ms** | **1h 55m** | 33.2 KB |
| **4xRealWebPhoto DAT-2** 🏆 | **DAT-2 (Vision Transformer 2024)** | **3 157.0 ms** | **8h 46m** | 41.7 KB |

---

## 📁 Czysta struktura katalogu `image_processing/` (wszystko potrzebne od zera)

```
image_processing/
├── README.md                          # Dokumentacja i instrukcja uruchomienia
├── .gitignore                         # Ignorowanie wag *.pth (>100MB)
├── benchmark.py                       # Silnik upscalingu: automatyczne pobieranie wag, inferencja PyTorch MPS i generowanie raportu
├── generate_all_methods_master.py     # Generator raportu HTML (tylko biblioteka standardowa Pythona)
├── models/                            # Wagi modeli (.pth: DAT-2, UltraSharp, Real-ESRGAN)
├── sample_images/                     # 15 oryginalnych zdjęć produktów (256x256 px)
└── outputs/
    ├── master_comparison_all_methods.html # Kompletny raport porównawczy
    ├── realwebphoto_dat2/             # Obrazy 1024px WebP wygenerowane modelem DAT-2
    ├── ultrasharp_x4/                 # Obrazy 1024px WebP wygenerowane modelem 4x-UltraSharp
    ├── realesrgan_x4plus/             # Obrazy 1024px WebP wygenerowane modelem Real-ESRGAN
    └── bicubic/                       # Obrazy 1024px WebP wygenerowane filtrem Lanczos
```

---

## 🛠️ Uruchomienie

### 1. Przetworzenie wszystkiego od zera (inferencja AI + raport):
Pobiera brakujące wagi modeli, przeprowadza upscaling na GPU MPS i tworzy raport:
```bash
.venv/bin/python image_processing/benchmark.py
```

### 2. Szybkie przebudowanie samego raportu HTML (błyskawiczne, bez GPU):
```bash
python3 image_processing/generate_all_methods_master.py
```

### 3. Podgląd raportu:
Otwórz w przeglądarce:
👉 `image_processing/outputs/master_comparison_all_methods.html`
