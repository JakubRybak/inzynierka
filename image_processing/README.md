# Image processing

DAT-2 + GFPGAN powiększa zdjęcia FashionGen czterokrotnie i rekonstruuje wykryte twarze. Pipeline zachowuje tło zdjęcia. Wyniki zapisuje jako WebP z ustawieniem jakości 90.

Z katalogu głównego repozytorium:

```bash
python -m pip install -r image_processing/requirements.txt
python -m image_processing data/processed/fashiongen/pilot_9922/selection.csv output/photos --photos main
```

Wejście może być plikiem CSV, Parquet lub JSONL. Jedyna wymagana kolumna to `product_id`. Zdjęcia są wybierane z manifestów `images_train.csv` i `images_validation.csv` w `data/processed/fashiongen/`.

- `--photos main` wybiera ujęcie `id_gridfs_1` każdego produktu.
- `--photos all` wybiera wszystkie ujęcia.
- Wagi są pobierane do `image_processing/models/`. Opcja `--weights-dir` pozwala wskazać inny katalog wag.
- `--device` pozwala wybrać MPS, CUDA lub CPU. Domyślnie wybór jest automatyczny.
- Poprawne zapisane pliki WebP są pomijane przy wznowieniu. Opcja `--force` wymusza ponowny zapis.

Ścieżka względna zdjęcia jest zachowana. Przykładowy wynik to `output/photos/images/train/87798/87798_id_gridfs_1.webp`.
