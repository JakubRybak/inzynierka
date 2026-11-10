#!/usr/bin/env python3
"""
Generate an enhanced visual comparison report (v2) for Super-Resolution methods:
1. Enlarged photos with fluid widescreen container (up to 1840px).
2. Side-cropping options (default 3:5 portrait, removes ~40% empty studio background).
3. Interactive column switcher (5 cols, 3 cols, 2 cols, 1 col) for huge side-by-side inspection.
4. Method toggle checkboxes to compare any 2-3 methods at giant scale.
5. Interactive full-resolution modal (A/B switcher with keyboard 1..5 navigation).
"""

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
SAMPLES_DIR = BASE_DIR / "sample_images"

METHODS = [
    {
        "id": "orig",
        "name": "Oryginał",
        "sub": "256×256 px · Pixelated",
        "folder": None,
        "format": "png",
        "badge_class": "orig-badge",
        "header_class": "orig-header",
        "res": "256×256",
        "time": "Baseline",
    },
    {
        "id": "lanczos",
        "name": "Lanczos + Unsharp",
        "sub": "1024×1024 px · Interpolation",
        "folder": "bicubic",
        "format": "webp",
        "badge_class": "lanczos-badge",
        "header_class": "lanczos-header",
        "res": "1024×1024",
        "time": "27.8 ms",
    },
    {
        "id": "realesrgan",
        "name": "Real-ESRGAN x4plus",
        "sub": "1024×1024 px · RRDBNet",
        "folder": "realesrgan_x4plus",
        "format": "webp",
        "badge_class": "realesrgan-badge",
        "header_class": "realesrgan-header",
        "res": "1024×1024",
        "time": "688.3 ms",
    },
    {
        "id": "ultra",
        "name": "4x-UltraSharp",
        "sub": "1024×1024 px · ESRGAN Fine-tuned",
        "folder": "ultrasharp_x4",
        "format": "webp",
        "badge_class": "ultra-badge",
        "header_class": "ultra-header",
        "res": "1024×1024",
        "time": "680.7 ms",
    },
    {
        "id": "dat2",
        "name": "4xRealWebPhoto DAT-2 🏆",
        "sub": "1024×1024 px · Transformer (2024)",
        "folder": "realwebphoto_dat2",
        "format": "webp",
        "badge_class": "dat2-badge",
        "header_class": "dat2-header highlight",
        "res": "1024×1024",
        "time": "3157.0 ms",
    },
]


def format_filesize(size_bytes: int) -> str:
    kb = size_bytes / 1024
    if kb >= 1000:
        return f"{kb/1024:.2f} MB"
    return f"{kb:.1f} KB"


def build_report():
    sample_images = sorted(SAMPLES_DIR.glob("*.png"))
    benchmark_json_path = OUTPUTS_DIR / "benchmark_results.json"
    bench_data = {}
    if benchmark_json_path.exists():
        with open(benchmark_json_path, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

    # Product cards HTML
    cards_html = []
    
    for idx, img_path in enumerate(sample_images):
        stem = img_path.stem
        parts = stem.split("_")
        cat_name = " ".join(parts[1:-1]).capitalize() if len(parts) >= 3 else stem
        pid = parts[-1] if len(parts) >= 3 else ""
        card_title = f"{idx+1}. {cat_name} (ID {pid})" if pid else f"{idx+1}. {cat_name}"

        # Collect images for this product
        thumbs_html = []
        for m in METHODS:
            m_id = m["id"]
            if m_id == "orig":
                rel_url = f"../sample_images/{img_path.name}"
                full_p = SAMPLES_DIR / img_path.name
            else:
                rel_url = f"{m['folder']}/{stem}.webp"
                full_p = OUTPUTS_DIR / m["folder"] / f"{stem}.webp"

            size_str = format_filesize(full_p.stat().st_size) if full_p.exists() else "N/A"

            thumb_block = f"""
                <div class="thumb col-{m_id}" data-method="{m_id}" onclick="openModal('{stem}', '{m_id}', '{card_title}')">
                    <div class="thumb-header {m['header_class']}">
                        <div class="th-title">{m['name']}</div>
                        <div class="th-sub">{m['res']} · {m['time']}</div>
                    </div>
                    <div class="thumb-media {'is-orig' if m_id == 'orig' else ''}">
                        <img src="{rel_url}" alt="{m['name']}" loading="lazy">
                        <span class="media-badge">{m['format'].upper()} {size_str}</span>
                        <div class="zoom-hint">🔍 Kliknij, aby powiększyć 1024px</div>
                    </div>
                </div>
            """
            thumbs_html.append(thumb_block)

        card_block = f"""
        <div class="product-card" id="card-{idx}">
            <div class="product-card-header">
                <h3>{card_title}</h3>
                <span class="quick-nav">Pozycja {idx+1} z {len(sample_images)}</span>
            </div>
            <div class="grid">
                {''.join(thumbs_html)}
            </div>
        </div>
        """
        cards_html.append(card_block)

    # Metrics table
    bench_rows = []
    if "methods" in bench_data:
        m_map = {
            "bicubic": "Lanczos + Unsharp (Classical Baseline)",
            "realesrgan_x4plus": "Real-ESRGAN x4plus",
            "ultrasharp_x4": "4x-UltraSharp",
            "realwebphoto_dat2": "4xRealWebPhoto (DAT-2) 🏆",
        }
        for k, name in m_map.items():
            if k in bench_data["methods"]:
                row = bench_data["methods"][k]
                bench_rows.append(f"""
                <tr>
                    <td><b>{row['name']}</b><br><small>{row['architecture']}</small></td>
                    <td><b>{row['avg_ms_per_image']} ms</b></td>
                    <td>{row['throughput_fps']} fps</td>
                    <td><b>{row['extrapolated_10k_minutes']} min</b> ({row['extrapolated_10k_hours']} h)</td>
                    <td><b>{row['avg_webp_size_kb']} KB</b> (PNG: {row['avg_png_size_kb']} KB)</td>
                </tr>
                """)

    html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Super-Resolution v2: Powiększone zdjęcia & Przycięte puste tło</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-card: #131b2e;
            --border: #223049;
            --border-hover: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-orange: #fb923c;
            --accent-purple: #c084fc;
            --crop-ratio: 3 / 5;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            padding-bottom: 100px;
        }}

        /* Aspect ratio crop variations */
        body.crop-3-5 {{ --crop-ratio: 3 / 5; }}
        body.crop-9-16 {{ --crop-ratio: 9 / 16; }}
        body.crop-3-4 {{ --crop-ratio: 3 / 4; }}
        body.crop-1-1 {{ --crop-ratio: 1 / 1; }}

        /* Top sticky controller */
        .topbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(9, 13, 22, 0.95);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .top-brand {{
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .top-brand span {{
            font-size: 11px;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-blue);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 2px 7px;
            border-radius: 4px;
        }}

        .controls-group {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .ctrl-section {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: #131b2e;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 4px 8px;
        }}

        .ctrl-label {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-right: 4px;
        }}

        .btn-toggle {{
            background: #1e293b;
            color: #cbd5e1;
            border: 1px solid #334155;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .btn-toggle:hover {{
            background: #273549;
            color: #ffffff;
            border-color: var(--accent-blue);
        }}
        .btn-toggle.active {{
            background: var(--accent-blue);
            color: #090d16;
            border-color: var(--accent-blue);
            font-weight: 700;
        }}

        .filter-toggle-wrap {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .filter-chip {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            color: #cbd5e1;
            cursor: pointer;
            user-select: none;
        }}
        .filter-chip input {{
            accent-color: var(--accent-blue);
            cursor: pointer;
        }}

        /* Main Container */
        .main-container {{
            width: 96%;
            max-width: 1840px;
            margin: 24px auto 0 auto;
        }}

        .hero-banner {{
            background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 22px 26px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .hero-banner h1 {{
            font-size: 20px;
            color: #ffffff;
            margin-bottom: 6px;
        }}
        .hero-banner p {{
            font-size: 13px;
            color: var(--text-muted);
            max-width: 900px;
            line-height: 1.5;
        }}

        /* Metrics Table */
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            background: #131b2e;
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 30px;
        }}
        .metrics-table th, .metrics-table td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }}
        .metrics-table th {{
            background: #0f172a;
            color: var(--text-muted);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* Product Cards */
        .product-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 28px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }}

        .product-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 1px solid #1e293b;
        }}
        .product-card-header h3 {{
            font-size: 17px;
            color: #ffffff;
            font-weight: 700;
        }}
        .quick-nav {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Dynamic Grid Layouts */
        .grid {{
            display: grid;
            gap: 16px;
            transition: all 0.2s ease;
        }}

        body.cols-5 .grid {{
            grid-template-columns: repeat(5, 1fr);
        }}
        body.cols-3 .grid {{
            grid-template-columns: repeat(3, 1fr);
        }}
        body.cols-2 .grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
        body.cols-1 .grid {{
            grid-template-columns: 1fr;
            max-width: 800px;
            margin: 0 auto;
        }}

        @media (max-width: 1300px) {{
            body.cols-5 .grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        @media (max-width: 850px) {{
            body.cols-5 .grid, body.cols-3 .grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 580px) {{
            body.cols-5 .grid, body.cols-3 .grid, body.cols-2 .grid {{ grid-template-columns: 1fr; }}
        }}

        /* Thumbnail Container */
        .thumb {{
            background: #090d16;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            cursor: pointer;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .thumb:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-blue);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45);
        }}

        .thumb.hidden {{
            display: none !important;
        }}

        /* Header above image */
        .thumb-header {{
            background: #101726;
            padding: 8px 10px;
            border-bottom: 1px solid var(--border);
            text-align: center;
        }}
        .thumb-header.highlight {{
            background: rgba(52, 211, 153, 0.12);
            border-bottom: 1px solid rgba(52, 211, 153, 0.3);
        }}
        .thumb-header.highlight .th-title {{
            color: var(--accent-green);
        }}
        .th-title {{
            font-size: 12px;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .th-sub {{
            font-size: 10px;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        /* Cropped media area */
        .thumb-media {{
            position: relative;
            width: 100%;
            aspect-ratio: var(--crop-ratio);
            overflow: hidden;
            background: #090d16;
        }}

        .thumb-media img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
            transition: transform 0.25s ease;
        }}

        /* 1:1 original square mode without cropping */
        body.crop-1-1 .thumb-media img {{
            object-fit: contain;
        }}

        .thumb-media.is-orig img {{
            image-rendering: pixelated;
        }}

        .thumb:hover .thumb-media img {{
            transform: scale(1.04);
        }}

        .media-badge {{
            position: absolute;
            bottom: 6px;
            right: 6px;
            background: rgba(9, 13, 22, 0.85);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #cbd5e1;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
            z-index: 5;
        }}

        .zoom-hint {{
            position: absolute;
            inset: 0;
            background: rgba(9, 13, 22, 0.45);
            backdrop-filter: blur(2px);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            opacity: 0;
            transition: opacity 0.15s ease;
            z-index: 6;
        }}
        .thumb:hover .zoom-hint {{
            opacity: 1;
        }}

        /* Interactive Modal Lightbox */
        .modal-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(5, 8, 14, 0.92);
            backdrop-filter: blur(16px);
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .modal-overlay.open {{
            display: flex;
        }}

        .modal-content {{
            background: #131b2e;
            border: 1px solid var(--border);
            border-radius: 14px;
            max-width: 1100px;
            width: 100%;
            max-height: 94vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        }}

        .modal-header {{
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #0f172a;
        }}
        .modal-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
        }}
        .modal-close {{
            background: #1e293b;
            color: #cbd5e1;
            border: 1px solid #334155;
            width: 32px;
            height: 32px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s ease;
        }}
        .modal-close:hover {{
            background: #ef4444;
            color: #ffffff;
            border-color: #ef4444;
        }}

        .modal-tabs {{
            display: flex;
            background: #0b1120;
            border-bottom: 1px solid var(--border);
            padding: 8px 16px;
            gap: 8px;
            overflow-x: auto;
        }}
        .modal-tab-btn {{
            background: #131b2e;
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 7px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}
        .modal-tab-btn:hover {{
            color: #ffffff;
            border-color: var(--accent-blue);
        }}
        .modal-tab-btn.active {{
            background: var(--accent-blue);
            color: #090d16;
            border-color: var(--accent-blue);
            font-weight: 700;
        }}
        .modal-tab-btn.active.is-dat2 {{
            background: var(--accent-green);
            border-color: var(--accent-green);
        }}

        .modal-body {{
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
            min-height: 500px;
            background: #070a10;
        }}
        .modal-img-wrap {{
            max-width: 900px;
            max-height: 75vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        .modal-img-wrap img {{
            max-width: 100%;
            max-height: 72vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        .modal-img-wrap.is-pixelated img {{
            image-rendering: pixelated;
        }}

        .modal-footer {{
            padding: 10px 20px;
            background: #0f172a;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body class="crop-3-5 cols-5">

    <!-- Sticky Top Controls Bar -->
    <div class="topbar">
        <div class="top-brand">
            SUPER-RESOLUTION <span>RAPORT V2 (POWIĘKSZONY & PRZYCIĘTY)</span>
        </div>

        <div class="controls-group">
            <!-- Crop aspect ratio buttons -->
            <div class="ctrl-section">
                <span class="ctrl-label">✂️ Kadrowanie (puste boki):</span>
                <button class="btn-toggle active" id="btn-crop-3-5" onclick="setCrop('3-5')">Sylwetka 3:5 (~40% wycięte)</button>
                <button class="btn-toggle" id="btn-crop-9-16" onclick="setCrop('9-16')">Wąskie 9:16</button>
                <button class="btn-toggle" id="btn-crop-3-4" onclick="setCrop('3-4')">Lekkie 3:4</button>
                <button class="btn-toggle" id="btn-crop-1-1" onclick="setCrop('1-1')">Kwadrat 1:1</button>
            </div>

            <!-- Column layout / Zoom buttons -->
            <div class="ctrl-section">
                <span class="ctrl-label">🔍 Rozmiar / Kolumny:</span>
                <button class="btn-toggle active" id="btn-cols-5" onclick="setCols(5)">5 Kolumn</button>
                <button class="btn-toggle" id="btn-cols-3" onclick="setCols(3)">3 Kolumny (Duże)</button>
                <button class="btn-toggle" id="btn-cols-2" onclick="setCols(2)">2 Kolumny (HD)</button>
                <button class="btn-toggle" id="btn-cols-1" onclick="setCols(1)">1 Kolumna (Max)</button>
            </div>

            <!-- Method filter checkboxes -->
            <div class="ctrl-section">
                <span class="ctrl-label">Kolumny:</span>
                <div class="filter-toggle-wrap">
                    <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('orig', this.checked)"> Orig</label>
                    <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('lanczos', this.checked)"> Lanczos</label>
                    <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('realesrgan', this.checked)"> ESRGAN</label>
                    <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('ultra', this.checked)"> UltraSharp</label>
                    <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('dat2', this.checked)"> DAT-2 🏆</label>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-container">

        <div class="hero-banner">
            <div>
                <h1>Wizualne porównanie metod Super-Resolution (M1 Pro 32 GB)</h1>
                <p>
                    Zdjęcia produktów zostały <b>powiększone</b> (kontener do 1840 px) oraz <b>przycięte po bokach</b> z domyślną proporcją <b>3:5</b>. 
                    Dzięki temu zlikwidowano ~40% zbędnego, pustego tła studyjnego z lewej i prawej strony, a tkaniny, szwy oraz twarze modeli są o <b>ponad 2.5x większe</b> na ekranie.
                    Możesz w każdej chwili zmienić kadrowanie na 9:16, 3:4 lub 1:1, albo włączyć 2-3 kolumny przyciskami powyżej.
                </p>
            </div>
            <div>
                <a href="storefront_comparison.html" style="background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600; display: inline-block;">
                    🛍️ Zobacz widok Storefrontu &rarr;
                </a>
            </div>
        </div>

        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Metoda / Architektura</th>
                    <th>Średni czas / zdjęcie</th>
                    <th>Przepustowość</th>
                    <th>Szacowany czas (10 000 produktów)</th>
                    <th>Średnia waga pliku WebP (PNG)</th>
                </tr>
            </thead>
            <tbody>
                {''.join(bench_rows)}
            </tbody>
        </table>

        <!-- Product Cards List -->
        {''.join(cards_html)}

    </div>

    <!-- Lightbox Modal -->
    <div class="modal-overlay" id="image-modal" onclick="closeModalOnBackdrop(event)">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modal-title">Podgląd HD</div>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-tabs">
                <button class="modal-tab-btn" id="mtab-orig" onclick="switchModalMethod('orig')">1. Oryginał (256px)</button>
                <button class="modal-tab-btn" id="mtab-lanczos" onclick="switchModalMethod('lanczos')">2. Lanczos (1024px)</button>
                <button class="modal-tab-btn" id="mtab-realesrgan" onclick="switchModalMethod('realesrgan')">3. Real-ESRGAN (1024px)</button>
                <button class="modal-tab-btn" id="mtab-ultra" onclick="switchModalMethod('ultra')">4. 4x-UltraSharp (1024px)</button>
                <button class="modal-tab-btn is-dat2" id="mtab-dat2" onclick="switchModalMethod('dat2')">5. DAT-2 🏆 (1024px)</button>
            </div>
            <div class="modal-body">
                <div class="modal-img-wrap" id="modal-img-container">
                    <img id="modal-img" src="" alt="Zoomed view">
                </div>
            </div>
            <div class="modal-footer">
                <div id="modal-status">Aktywna metoda: DAT-2</div>
                <div>Naciśnij <b>1, 2, 3, 4, 5</b> na klawiaturze, aby błyskawicznie porównać metody w miejscu | <b>ESC</b> zamyka</div>
            </div>
        </div>
    </div>

    <script>
        let currentStem = '';
        let currentMethod = 'dat2';
        let currentTitle = '';

        function setCrop(ratio) {{
            document.body.classList.remove('crop-3-5', 'crop-9-16', 'crop-3-4', 'crop-1-1');
            document.body.classList.add('crop-' + ratio);
            
            document.querySelectorAll('[id^="btn-crop-"]').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById('btn-crop-' + ratio);
            if (btn) btn.classList.add('active');
        }}

        function setCols(n) {{
            document.body.classList.remove('cols-5', 'cols-3', 'cols-2', 'cols-1');
            document.body.classList.add('cols-' + n);

            document.querySelectorAll('[id^="btn-cols-"]').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById('btn-cols-' + n);
            if (btn) btn.classList.add('active');
        }}

        function toggleMethod(methodId, visible) {{
            const elements = document.querySelectorAll('.col-' + methodId);
            elements.forEach(el => {{
                if (visible) {{
                    el.classList.remove('hidden');
                }} else {{
                    el.classList.add('hidden');
                }}
            }});
        }}

        // Modal Lightbox
        const methodPaths = {{
            'orig': (stem) => '../sample_images/' + stem + '.png',
            'lanczos': (stem) => 'bicubic/' + stem + '.webp',
            'realesrgan': (stem) => 'realesrgan_x4plus/' + stem + '.webp',
            'ultra': (stem) => 'ultrasharp_x4/' + stem + '.webp',
            'dat2': (stem) => 'realwebphoto_dat2/' + stem + '.webp'
        }};

        const methodNames = {{
            'orig': 'Oryginał (256×256 px - piksele widoczne w 100% skali)',
            'lanczos': 'Lanczos + Unsharp (1024×1024 px - interpolacja)',
            'realesrgan': 'Real-ESRGAN x4plus (1024×1024 px - RRDBNet)',
            'ultra': '4x-UltraSharp (1024×1024 px - mikro-tekstury)',
            'dat2': '4xRealWebPhoto DAT-2 🏆 (1024×1024 px - Transformer)'
        }};

        function openModal(stem, methodId, title) {{
            currentStem = stem;
            currentMethod = methodId;
            currentTitle = title;
            document.getElementById('modal-title').innerText = title;
            updateModalView();
            document.getElementById('image-modal').classList.add('open');
        }}

        function switchModalMethod(methodId) {{
            currentMethod = methodId;
            updateModalView();
        }}

        function updateModalView() {{
            const imgEl = document.getElementById('modal-img');
            const containerEl = document.getElementById('modal-img-container');
            const urlGen = methodPaths[currentMethod];
            if (urlGen) {{
                imgEl.src = urlGen(currentStem);
            }}

            if (currentMethod === 'orig') {{
                containerEl.classList.add('is-pixelated');
            }} else {{
                containerEl.classList.remove('is-pixelated');
            }}

            document.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById('mtab-' + currentMethod);
            if (activeBtn) activeBtn.classList.add('active');

            document.getElementById('modal-status').innerText = 'Aktywna metoda: ' + (methodNames[currentMethod] || currentMethod);
        }}

        function closeModal() {{
            document.getElementById('image-modal').classList.remove('open');
        }}

        function closeModalOnBackdrop(e) {{
            if (e.target.id === 'image-modal') {{
                closeModal();
            }}
        }}

        // Keyboard hotkeys
        window.addEventListener('keydown', (e) => {{
            const modalOpen = document.getElementById('image-modal').classList.contains('open');
            if (e.key === 'Escape' && modalOpen) {{
                closeModal();
                return;
            }}
            if (modalOpen) {{
                if (e.key === '1') switchModalMethod('orig');
                if (e.key === '2') switchModalMethod('lanczos');
                if (e.key === '3') switchModalMethod('realesrgan');
                if (e.key === '4') switchModalMethod('ultra');
                if (e.key === '5') switchModalMethod('dat2');
            }}
        }});
    </script>
</body>
</html>
"""

    report_v2_path = OUTPUTS_DIR / "comparison_report_v2.html"
    with open(report_v2_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Generated: {report_v2_path}")

    # Also update comparison_report.html so either file opened reflects the latest changes
    report_orig_path = OUTPUTS_DIR / "comparison_report.html"
    with open(report_orig_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Updated: {report_orig_path}")


if __name__ == "__main__":
    build_report()
