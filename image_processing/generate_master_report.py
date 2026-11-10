#!/usr/bin/env python3
"""
Generate an all-in-one Master Comparison HTML suite:
1. Section 1: Side-by-side product comparison (all 5 methods next to each other per product).
2. Section 2: Storefront catalogue comparison (all products grouped by method, with live in-place tab flip).
3. Sticky global controller with:
   - Main view switcher buttons (Product Comparison vs Storefront vs Both).
   - Side cropping buttons (3:5, 9:16, 3:4, 1:1).
   - Photo background tone buttons (#ededf0 soft grey, #e2e4e8 medium, #edeae4 warm, #ffffff white).
   - Column layout buttons (5, 4, 3, 2 cols).
   - Page theme toggle (Dark Studio vs Light Storefront).
   - Method filter checkboxes.
4. Interactive 1024px Lightbox modal with instant 1..5 hotkey switching.
"""

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
SAMPLES_DIR = BASE_DIR / "sample_images"

METADATA = {
    "86605": {"brand": "Diesel", "category": "Jackets", "title": "Leather Biker Jacket", "price": "$335"},
    "86933": {"brand": "Thom Browne", "category": "Knit Sweaters", "title": "Wool Knit Sweater", "price": "$970"},
    "87389": {"brand": "Givenchy", "category": "T-shirts", "title": "Graphic Print T-Shirt", "price": "$970"},
    "86877": {"brand": "Rag & Bone", "category": "Dresses", "title": "Silk Sleeveless Dress", "price": "$595"},
    "86779": {"brand": "Dsquared2", "category": "Shirts", "title": "Tailored Check Shirt", "price": "$645"},
    "86773": {"brand": "Dsquared2", "category": "Jeans", "title": "Distressed Denim Jeans", "price": "$630"},
    "99750": {"brand": "Comme des Garçons", "category": "Classic Coats", "title": "Classic Wool Coat", "price": "$2,615"},
    "88112": {"brand": "MM6 Maison Margiela", "category": "Hoodies & Zipups", "title": "Oversized Cotton Hoodie", "price": "$385"},
    "91440": {"brand": "MSGM", "category": "Sweatshirts", "title": "Crewneck Fleece Sweatshirt", "price": "$245"},
    "87053": {"brand": "Lanvin", "category": "Bombers", "title": "Satin Bomber Jacket", "price": "$1,595"},
    "86810": {"brand": "Dsquared2", "category": "Trousers", "title": "Tailored Slim Trousers", "price": "$495"},
    "89767": {"brand": "Carven", "category": "Skirts", "title": "Pleated A-Line Skirt", "price": "$530"},
    "90103": {"brand": "D.Gnak by Kang.D", "category": "Cardigans", "title": "Draped Open Cardigan", "price": "$455"},
    "87937": {"brand": "T by Alexander Wang", "category": "Blouses", "title": "Silk V-Neck Blouse", "price": "$225"},
    "87953": {"brand": "Band of Outsiders", "category": "Polos", "title": "Pique Cotton Polo Shirt", "price": "$145"},
}

METHODS = [
    {
        "id": "orig",
        "name": "Oryginał",
        "sub": "256×256 px · Piksele",
        "folder": None,
        "format": "png",
        "header_class": "orig-header",
        "res": "256×256",
        "time": "Baseline",
    },
    {
        "id": "lanczos",
        "name": "Lanczos + Unsharp",
        "sub": "1024×1024 px · Interpolacja",
        "folder": "bicubic",
        "format": "webp",
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


def build_master():
    sample_images = sorted(SAMPLES_DIR.glob("*.png"))
    benchmark_json_path = OUTPUTS_DIR / "benchmark_results.json"
    bench_data = {}
    if benchmark_json_path.exists():
        with open(benchmark_json_path, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

    # 1. SECTION 1: Product-by-Product Comparison
    sec1_cards = []
    for idx, img_path in enumerate(sample_images):
        stem = img_path.stem
        parts = stem.split("_")
        pid = parts[-1]
        meta = METADATA.get(pid, {
            "brand": "FashionGen",
            "category": parts[1].capitalize(),
            "title": f"Product {pid}",
            "price": "$250"
        })
        card_title = f"{idx+1}. {meta['brand']} — {meta['title']} ({meta['category']}, ID {pid})"

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
                <div class="thumb col-{m_id}" data-method="{m_id}" onclick="openModal('{stem}', '{m_id}', '{meta['brand']} — {meta['title']}')">
                    <div class="thumb-header {m['header_class']}">
                        <div class="th-title">{m['name']}</div>
                        <div class="th-sub">{m['res']} · {m['time']}</div>
                    </div>
                    <div class="thumb-media {'is-orig' if m_id == 'orig' else ''}">
                        <img src="{rel_url}" alt="{m['name']}" loading="lazy">
                        <span class="media-badge">{m['format'].upper()} {size_str}</span>
                        <div class="zoom-hint">🔍 Kliknij powiększenie 1024px</div>
                    </div>
                </div>
            """
            thumbs_html.append(thumb_block)

        card_block = f"""
        <div class="product-card" id="card-{idx}">
            <div class="product-card-header">
                <div class="pch-left">
                    <h3>{card_title}</h3>
                    <div class="pch-meta">{meta['price']} · Kolekcja FashionGen</div>
                </div>
                <span class="quick-nav">Produkt {idx+1} z {len(sample_images)}</span>
            </div>
            <div class="grid comparison-grid">
                {''.join(thumbs_html)}
            </div>
        </div>
        """
        sec1_cards.append(card_block)

    # 2. SECTION 2: Storefront Catalogue grouped by method
    sec2_sections = []
    storefront_configs = [
        ("orig", "1. Oryginały (Stan obecny w repozytorium)", "Rozdzielczość 256×256 px. Zwróć uwagę na rozmycie w kartach sklepu.", "256 × 256 px", "~45 KB (PNG)", "Niska (rozmyta)", "orig-header", "orig-section"),
        ("lanczos", "2. Lanczos + Unsharp (Klasyczna interpolacja)", "Podniesienie do 1024×1024 z filtrem wyostrzającym. Szybki baseline.", "1024 × 1024 px", "~24 KB (WebP)", "Średnia (widoczne artefakty krawędzi)", "lanczos-header", ""),
        ("realesrgan", "3. Real-ESRGAN x4plus (Klasyczny model CNN RRDBNet)", "Model sieci neuronowej GAN/CNN. Wygładza szumy, ale może dawać efekt plastiku.", "1024 × 1024 px", "~33 KB (WebP)", "Dobra (lekko sztuczna faktura)", "realesrgan-header", ""),
        ("ultra", "4. 4x-UltraSharp (Model CNN zoptymalizowany pod mikro-tekstury)", "Agresywniejsze wyciąganie mikro-detali i splotów tkanin.", "1024 × 1024 px", "~47 KB (WebP)", "Bardzo dobra (ostra)", "ultra-header", ""),
        ("dat2", "5. 4xRealWebPhoto DAT-2 🏆 (Vision Transformer SOTA 2024/2025)", "Model transformatorowy. Najbardziej naturalne zagniecenia, cienie i twarze.", "1024 × 1024 px", "~42 KB (WebP)", "Wybitna (fotorealizm e-commerce)", "dat2-header", ""),
    ]

    for m_id, title, desc, res_val, size_val, qual_val, header_cls, extra_sec_cls in storefront_configs:
        sf_cards = []
        for img_path in sample_images:
            stem = img_path.stem
            parts = stem.split("_")
            pid = parts[-1]
            meta = METADATA.get(pid, {
                "brand": "FashionGen",
                "category": parts[1].capitalize(),
                "title": f"Product {pid}",
                "price": "$250"
            })

            if m_id == "orig":
                img_src = f"../sample_images/{img_path.name}"
                badge_lbl = "256 px"
                is_orig_cls = "is-orig"
            else:
                m_folder = next(m["folder"] for m in METHODS if m["id"] == m_id)
                img_src = f"{m_folder}/{stem}.webp"
                badge_lbl = "1024 px"
                is_orig_cls = ""

            full_p = (OUTPUTS_DIR / m_folder / f"{stem}.webp") if m_id != "orig" else (SAMPLES_DIR / img_path.name)
            size_badge = format_filesize(full_p.stat().st_size) if full_p.exists() else ""

            card_html = f"""
            <div class="sf-product-card" onclick="openModal('{stem}', '{m_id}', '{meta['brand']} — {meta['title']}')">
                <div class="sf-media {is_orig_cls}">
                    <span class="media-badge">{badge_lbl} · {size_badge}</span>
                    <img src="{img_src}" alt="{meta['title']}" loading="lazy">
                    <div class="zoom-hint">🔍 Podgląd HD</div>
                </div>
                <div class="sf-info">
                    <div class="sf-brand">{meta['brand']}</div>
                    <div class="sf-title">{meta['title']}</div>
                    <div class="sf-category">{meta['category']}</div>
                    <div class="sf-price">{meta['price']}</div>
                </div>
            </div>
            """
            sf_cards.append(card_html)

        sec_block = f"""
        <div class="sf-section-box {extra_sec_cls}" id="sf-sec-{m_id}">
            <div class="sf-section-header {header_cls}">
                <div class="sf-header-title">
                    <h2>{title}</h2>
                    <p>{desc}</p>
                </div>
                <div class="sf-header-stats">
                    <div class="stat-badge"><span>Rozdzielczość:</span><b>{res_val}</b></div>
                    <div class="stat-badge"><span>Średni rozmiar:</span><b>{size_val}</b></div>
                    <div class="stat-badge"><span>Ocena jakości:</span><b>{qual_val}</b></div>
                </div>
            </div>
            <div class="grid sf-grid">
                {''.join(sf_cards)}
            </div>
        </div>
        """
        sec2_sections.append(sec_block)

    # Benchmark metrics rows
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
    <title>E-commerce Super-Resolution: Master Suite (Porównanie + Storefront)</title>
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
            --photo-bg: #ededf0;
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
            padding-bottom: 120px;
            transition: background-color 0.2s ease, color 0.2s ease;
        }}

        /* Aspect ratio crop variations */
        body.crop-3-5 {{ --crop-ratio: 3 / 5; }}
        body.crop-9-16 {{ --crop-ratio: 9 / 16; }}
        body.crop-3-4 {{ --crop-ratio: 3 / 4; }}
        body.crop-1-1 {{ --crop-ratio: 1 / 1; }}

        /* Photo background tones */
        body.pbg-grey-soft {{ --photo-bg: #ededf0; }}
        body.pbg-grey-medium {{ --photo-bg: #e2e4e8; }}
        body.pbg-grey-warm {{ --photo-bg: #edeae4; }}
        body.pbg-white {{ --photo-bg: #ffffff; }}

        /* Light E-commerce Page Theme */
        body.theme-light {{
            --bg-body: #f4f5f7;
            --bg-card: #ffffff;
            --border: #e2e8f0;
            --border-hover: #0284c7;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }}
        body.theme-light .topbar {{
            background: rgba(244, 245, 247, 0.96);
            border-bottom: 1px solid #cbd5e1;
        }}
        body.theme-light .top-brand {{
            color: #0f172a;
        }}
        body.theme-light .ctrl-section {{
            background: #ffffff;
            border-color: #cbd5e1;
        }}
        body.theme-light .btn-toggle, body.theme-light .subnav-btn {{
            background: #f8fafc;
            color: #334155;
            border-color: #cbd5e1;
        }}
        body.theme-light .btn-toggle:hover, body.theme-light .subnav-btn:hover {{
            background: #e2e8f0;
            color: #0f172a;
            border-color: #0284c7;
        }}
        body.theme-light .btn-toggle.active, body.theme-light .subnav-btn.active {{
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
        }}
        body.theme-light .view-switch-btn.active {{
            background: #0284c7;
            color: #ffffff;
        }}
        body.theme-light .hero-banner {{
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-color: #e2e8f0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        body.theme-light .hero-banner h1, body.theme-light .product-card-header h3 {{
            color: #0f172a;
        }}
        body.theme-light .product-card, body.theme-light .sf-product-card, body.theme-light .sf-section-header {{
            background: #ffffff;
            border-color: #e2e8f0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        }}
        body.theme-light .sf-section-header h2 {{
            color: #0f172a;
        }}
        body.theme-light .product-card-header {{
            border-bottom-color: #f1f5f9;
        }}
        body.theme-light .thumb {{
            background: #ffffff;
            border-color: #e2e8f0;
        }}
        body.theme-light .thumb-header {{
            background: #f1f5f9;
            border-color: #e2e8f0;
        }}
        body.theme-light .th-title, body.theme-light .sf-title, body.theme-light .sf-price {{
            color: #0f172a;
        }}
        body.theme-light .metrics-table {{
            background: #ffffff;
            border-color: #e2e8f0;
        }}
        body.theme-light .metrics-table th {{
            background: #f8fafc;
            color: #64748b;
        }}
        body.theme-light .metrics-table td {{
            color: #1e293b;
            border-color: #f1f5f9;
        }}

        /* Sticky Topbar */
        .topbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(9, 13, 22, 0.95);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--border);
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
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

        /* View Switcher Main Tabs */
        .view-switch-wrap {{
            display: flex;
            background: #0f172a;
            border: 1px solid #334155;
            padding: 3px;
            border-radius: 9px;
            gap: 4px;
        }}
        .view-switch-btn {{
            background: transparent;
            color: var(--text-muted);
            border: none;
            padding: 7px 14px;
            border-radius: 7px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .view-switch-btn:hover {{
            color: #ffffff;
        }}
        .view-switch-btn.active {{
            background: var(--accent-blue);
            color: #090d16;
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.35);
        }}

        .controls-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .ctrl-section {{
            display: flex;
            align-items: center;
            gap: 4px;
            background: #131b2e;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 3px 6px;
        }}

        .ctrl-label {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-right: 2px;
        }}

        .btn-toggle {{
            background: #1e293b;
            color: #cbd5e1;
            border: 1px solid #334155;
            padding: 5px 9px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
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

        /* Secondary Sticky Navigation Bar for Active View */
        .subbar {{
            position: sticky;
            top: 55px;
            z-index: 990;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            padding: 8px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .subnav-links {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .subnav-btn {{
            background: var(--bg-card);
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .subnav-btn:hover {{
            color: #ffffff;
            border-color: var(--accent-blue);
        }}
        .subnav-btn.active {{
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

        /* Container */
        .main-container {{
            width: 96%;
            max-width: 1840px;
            margin: 20px auto 0 auto;
        }}

        /* Hero Banner */
        .hero-banner {{
            background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .hero-banner h1 {{
            font-size: 19px;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .hero-banner p {{
            font-size: 13px;
            color: var(--text-muted);
            max-width: 1000px;
            line-height: 1.5;
        }}

        /* Metrics Table Collapsible */
        details.metrics-accordion {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 24px;
            overflow: hidden;
        }}
        details.metrics-accordion summary {{
            padding: 12px 18px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            color: var(--accent-blue);
            background: #0f172a;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        details.metrics-accordion[open] summary {{
            border-bottom: 1px solid var(--border);
        }}
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .metrics-table th, .metrics-table td {{
            padding: 10px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 12px;
        }}
        .metrics-table th {{
            background: #0f172a;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 11px;
        }}

        /* Grids */
        .grid {{
            display: grid;
            gap: 16px;
            transition: all 0.2s ease;
        }}

        body.cols-5 .comparison-grid {{ grid-template-columns: repeat(5, 1fr); }}
        body.cols-4 .comparison-grid {{ grid-template-columns: repeat(4, 1fr); }}
        body.cols-3 .comparison-grid {{ grid-template-columns: repeat(3, 1fr); }}
        body.cols-2 .comparison-grid {{ grid-template-columns: repeat(2, 1fr); }}

        body.cols-5 .sf-grid {{ grid-template-columns: repeat(5, 1fr); }}
        body.cols-4 .sf-grid {{ grid-template-columns: repeat(4, 1fr); }}
        body.cols-3 .sf-grid {{ grid-template-columns: repeat(3, 1fr); }}
        body.cols-2 .sf-grid {{ grid-template-columns: repeat(2, 1fr); }}

        @media (max-width: 1300px) {{
            body.cols-5 .comparison-grid, body.cols-5 .sf-grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        @media (max-width: 850px) {{
            body.cols-5 .comparison-grid, body.cols-5 .sf-grid,
            body.cols-4 .comparison-grid, body.cols-4 .sf-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 580px) {{
            body.cols-5 .comparison-grid, body.cols-5 .sf-grid,
            body.cols-3 .comparison-grid, body.cols-3 .sf-grid,
            body.cols-2 .comparison-grid, body.cols-2 .sf-grid {{ grid-template-columns: 1fr; }}
        }}

        /* SECTION 1: Product-by-product Cards */
        .product-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            scroll-margin-top: 115px;
        }}
        .product-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid #1e293b;
        }}
        .pch-left h3 {{
            font-size: 16px;
            color: #ffffff;
            font-weight: 700;
        }}
        .pch-meta {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .quick-nav {{
            font-size: 11px;
            color: var(--text-muted);
            background: #0f172a;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid var(--border);
        }}

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

        .thumb-header {{
            background: #101726;
            padding: 7px 8px;
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
            margin-top: 1px;
        }}

        /* Media Area (Shared between Section 1 and Section 2) */
        .thumb-media, .sf-media {{
            position: relative;
            width: 100%;
            aspect-ratio: var(--crop-ratio);
            overflow: hidden;
            background-color: var(--photo-bg);
            isolation: isolate;
            transition: background-color 0.2s ease;
        }}

        .thumb-media img, .sf-media img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
            mix-blend-mode: multiply;
            transition: transform 0.25s ease;
        }}

        body.pbg-white .thumb-media img, body.pbg-white .sf-media img {{
            mix-blend-mode: normal;
        }}

        body.crop-1-1 .thumb-media img, body.crop-1-1 .sf-media img {{
            object-fit: contain;
        }}

        .thumb-media.is-orig img, .sf-media.is-orig img {{
            image-rendering: pixelated;
        }}

        .thumb:hover .thumb-media img, .sf-product-card:hover .sf-media img {{
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
        .thumb:hover .zoom-hint, .sf-product-card:hover .zoom-hint {{
            opacity: 1;
        }}

        /* SECTION 2: Storefront Catalogue Styles */
        .sf-section-box {{
            margin-bottom: 50px;
            scroll-margin-top: 115px;
        }}
        .sf-section-header {{
            background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }}
        .sf-section-header.orig-header {{ border-left: 5px solid var(--accent-orange); }}
        .sf-section-header.lanczos-header {{ border-left: 5px solid #64748b; }}
        .sf-section-header.realesrgan-header {{ border-left: 5px solid var(--accent-purple); }}
        .sf-section-header.ultra-header {{ border-left: 5px solid var(--accent-blue); }}
        .sf-section-header.dat2-header {{ border-left: 5px solid var(--accent-green); }}

        .sf-header-title h2 {{
            font-size: 17px;
            color: #ffffff;
            margin-bottom: 3px;
        }}
        .sf-header-title p {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .sf-header-stats {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .stat-badge {{
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid #334155;
            padding: 5px 10px;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            gap: 2px;
            font-size: 11px;
        }}
        .stat-badge b {{
            color: #ffffff;
            font-size: 12px;
        }}

        .sf-product-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            cursor: pointer;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .sf-product-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent-blue);
            box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.5);
        }}
        .sf-info {{
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            flex-grow: 1;
        }}
        .sf-brand {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent-blue);
        }}
        .sf-title {{
            font-size: 13px;
            font-weight: 600;
            color: #ffffff;
            line-height: 1.3;
        }}
        .sf-category {{
            font-size: 11px;
            color: var(--text-muted);
        }}
        .sf-price {{
            margin-top: 5px;
            font-size: 13px;
            font-weight: 700;
            color: #ffffff;
        }}

        /* Live tab flip mode in Storefront */
        body.sf-tab-mode .sf-section-box {{
            display: none;
            margin-bottom: 0;
        }}
        body.sf-tab-mode .sf-section-box.active-tab {{
            display: block;
        }}

        /* Main View Switcher Visibility */
        .view-section {{
            display: none;
        }}
        .view-section.active-view {{
            display: block;
        }}

        /* Lightbox Modal */
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
            background-color: var(--photo-bg);
            isolation: isolate;
            border-radius: 8px;
            overflow: hidden;
            padding: 6px;
            transition: background-color 0.2s ease;
        }}
        .modal-img-wrap img {{
            max-width: 100%;
            max-height: 72vh;
            object-fit: contain;
            border-radius: 6px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            mix-blend-mode: multiply;
        }}
        body.pbg-white .modal-img-wrap img {{
            mix-blend-mode: normal;
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
<body class="crop-3-5 cols-5 pbg-grey-soft">

    <!-- 1. STICKY TOPBAR -->
    <div class="topbar">
        <div class="top-brand">
            FASHION STORE <span>SUPER-RESOLUTION MASTER SUITE</span>
        </div>

        <!-- MAIN VIEW SWITCHER -->
        <div class="view-switch-wrap">
            <button class="view-switch-btn active" id="btn-view-comparison" onclick="switchMainView('comparison')">
                👥 1. Porównanie Produktów
            </button>
            <button class="view-switch-btn" id="btn-view-storefront" onclick="switchMainView('storefront')">
                🛍️ 2. Pełny Storefront
            </button>
            <button class="view-switch-btn" id="btn-view-both" onclick="switchMainView('both')">
                📑 Pokaż Obie Sekcje
            </button>
        </div>

        <!-- GLOBAL CONTROLS -->
        <div class="controls-group">
            <!-- Photo background tones -->
            <div class="ctrl-section">
                <span class="ctrl-label">🎨 Tło:</span>
                <button class="btn-toggle active" id="btn-pbg-grey-soft" onclick="setPhotoBg('grey-soft')">Szare (#ededf0)</button>
                <button class="btn-toggle" id="btn-pbg-grey-medium" onclick="setPhotoBg('grey-medium')">Średnie</button>
                <button class="btn-toggle" id="btn-pbg-grey-warm" onclick="setPhotoBg('grey-warm')">Ciepłe</button>
                <button class="btn-toggle" id="btn-pbg-white" onclick="setPhotoBg('white')">Białe 100%</button>
            </div>

            <!-- Crop aspect ratio -->
            <div class="ctrl-section">
                <span class="ctrl-label">✂️ Boki:</span>
                <button class="btn-toggle active" id="btn-crop-3-5" onclick="setCrop('3-5')">3:5 (~40% wycięte)</button>
                <button class="btn-toggle" id="btn-crop-9-16" onclick="setCrop('9-16')">9:16</button>
                <button class="btn-toggle" id="btn-crop-3-4" onclick="setCrop('3-4')">3:4</button>
                <button class="btn-toggle" id="btn-crop-1-1" onclick="setCrop('1-1')">1:1</button>
            </div>

            <!-- Columns layout -->
            <div class="ctrl-section">
                <span class="ctrl-label">🔍 Kolumny:</span>
                <button class="btn-toggle active" id="btn-cols-5" onclick="setCols(5)">5</button>
                <button class="btn-toggle" id="btn-cols-4" onclick="setCols(4)">4</button>
                <button class="btn-toggle" id="btn-cols-3" onclick="setCols(3)">3</button>
                <button class="btn-toggle" id="btn-cols-2" onclick="setCols(2)">2 (HD)</button>
            </div>

            <!-- Page Theme -->
            <div class="ctrl-section">
                <span class="ctrl-label">🌓 Motyw:</span>
                <button class="btn-toggle active" id="btn-theme-dark" onclick="setTheme('dark')">🌙 Ciemny</button>
                <button class="btn-toggle" id="btn-theme-light" onclick="setTheme('light')">☀️ Jasny</button>
            </div>
        </div>
    </div>

    <!-- 2. SECONDARY SUBBAR (Dynamic for Active View) -->
    <div class="subbar" id="subbar-comparison">
        <div style="font-size: 12px; font-weight: 700; color: var(--accent-blue); display: flex; align-items: center; gap: 6px;">
            <span>👥 Sekcja 1: Porównanie tych samych produktów z innymi metodami obok siebie</span>
        </div>
        <div class="filter-toggle-wrap">
            <span class="ctrl-label">Widoczne metody w wierszu:</span>
            <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('orig', this.checked)"> Orig</label>
            <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('lanczos', this.checked)"> Lanczos</label>
            <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('realesrgan', this.checked)"> ESRGAN</label>
            <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('ultra', this.checked)"> UltraSharp</label>
            <label class="filter-chip"><input type="checkbox" checked onchange="toggleMethod('dat2', this.checked)"> DAT-2 🏆</label>
        </div>
    </div>

    <div class="subbar" id="subbar-storefront" style="display: none;">
        <div class="subnav-links">
            <span class="ctrl-label" style="align-self: center; margin-right: 4px;">Skocz do metody:</span>
            <a href="#sf-sec-orig" class="subnav-btn" id="sbtn-orig" onclick="selectSfTab('sf-sec-orig')"><b>1.</b> Oryginały</a>
            <a href="#sf-sec-lanczos" class="subnav-btn" id="sbtn-lanczos" onclick="selectSfTab('sf-sec-lanczos')"><b>2.</b> Lanczos</a>
            <a href="#sf-sec-realesrgan" class="subnav-btn" id="sbtn-realesrgan" onclick="selectSfTab('sf-sec-realesrgan')"><b>3.</b> Real-ESRGAN</a>
            <a href="#sf-sec-ultra" class="subnav-btn" id="sbtn-ultra" onclick="selectSfTab('sf-sec-ultra')"><b>4.</b> 4x-UltraSharp</a>
            <a href="#sf-sec-dat2" class="subnav-btn" id="sbtn-dat2" onclick="selectSfTab('sf-sec-dat2')"><b>5.</b> DAT-2 🏆</a>
        </div>
        <div>
            <button class="btn-toggle" id="btn-toggle-sf-mode" onclick="toggleStorefrontMode()">
                🔄 Przełącz tryb: Zakładki w miejscu
            </button>
        </div>
    </div>

    <!-- MAIN WRAPPER -->
    <div class="main-container">

        <!-- Top Hero Overview -->
        <div class="hero-banner">
            <div>
                <h1>Zbiorczy raport Super-Resolution (Apple M1 Pro 32 GB)</h1>
                <p>
                    Połączony widok: <b>Sekcja 1</b> pozwala porównać konkretny produkt we wszystkich metodach obok siebie, a <b>Sekcja 2</b> pozwala ocenić spójność całego katalogu 15 produktów w ramach każdej metody.
                    Tło zdjęć zostało zmiękczone do naturalnego szarego odcienia studyjnego (<code>#ededf0</code>), a boki przycięte (3:5).
                </p>
            </div>
        </div>

        <!-- Collapsible Benchmark Summary Table -->
        <details class="metrics-accordion" open>
            <summary>
                <span>📊 Tabela wydajności i przepustowości (kliknij, aby zwinąć/rozwinąć)</span>
                <span style="font-size: 11px; font-weight: normal; color: var(--text-muted)">Akceleracja: MPS (Metal) · 15 produktów</span>
            </summary>
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
        </details>

        <!-- ========================================================= -->
        <!-- SEKCJA 1: PORÓWNANIE TYCH SAMYCH PRODUKTÓW OBOK SIEBIE    -->
        <!-- ========================================================= -->
        <section class="view-section active-view" id="view-comparison">
            <div style="margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
                <h2 style="font-size: 18px; color: #ffffff;">👥 Sekcja 1: Porównanie produktów (Wszystkie metody obok siebie)</h2>
                <span style="font-size: 12px; color: var(--text-muted);">Łącznie 15 produktów × 5 wariantów = 75 ujęć</span>
            </div>
            {''.join(sec1_cards)}
        </section>

        <!-- ========================================================= -->
        <!-- SEKCJA 2: SUBSEKCJE Z WSZYSTKIMI PRODUKTAMI DANEJ METODY  -->
        <!-- ========================================================= -->
        <section class="view-section" id="view-storefront">
            <div style="margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
                <h2 style="font-size: 18px; color: #ffffff;">🛍️ Sekcja 2: Pełny Storefront (Katalog podzielony na subsekcje metod)</h2>
                <span style="font-size: 12px; color: var(--text-muted);">Pozwala ocenić całościowy wygląd siatki sklepu</span>
            </div>
            {''.join(sec2_sections)}
        </section>

    </div>

    <!-- LIGHTBOX MODAL -->
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
        let currentMainView = 'comparison';
        let isSfTabMode = false;
        let currentStem = '';
        let currentMethod = 'dat2';

        // 1. Main View Switching (Section 1 vs Section 2 vs Both)
        function switchMainView(view) {{
            currentMainView = view;
            const secComp = document.getElementById('view-comparison');
            const secStore = document.getElementById('view-storefront');
            const subbarComp = document.getElementById('subbar-comparison');
            const subbarStore = document.getElementById('subbar-storefront');

            document.querySelectorAll('.view-switch-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById('btn-view-' + view);
            if (activeBtn) activeBtn.classList.add('active');

            if (view === 'comparison') {{
                secComp.classList.add('active-view');
                secStore.classList.remove('active-view');
                subbarComp.style.display = 'flex';
                subbarStore.style.display = 'none';
            }} else if (view === 'storefront') {{
                secComp.classList.remove('active-view');
                secStore.classList.add('active-view');
                subbarComp.style.display = 'none';
                subbarStore.style.display = 'flex';
            }} else if (view === 'both') {{
                secComp.classList.add('active-view');
                secStore.classList.add('active-view');
                subbarComp.style.display = 'flex';
                subbarStore.style.display = 'flex';
            }}
            window.scrollTo({{ top: 0, behavior: 'instant' }});
        }}

        // 2. Photo Background Controller
        function setPhotoBg(tone) {{
            document.body.classList.remove('pbg-grey-soft', 'pbg-grey-medium', 'pbg-grey-warm', 'pbg-white');
            document.body.classList.add('pbg-' + tone);

            document.querySelectorAll('[id^="btn-pbg-"]').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById('btn-pbg-' + tone);
            if (btn) btn.classList.add('active');
        }}

        // 3. Side Crop Controller
        function setCrop(ratio) {{
            document.body.classList.remove('crop-3-5', 'crop-9-16', 'crop-3-4', 'crop-1-1');
            document.body.classList.add('crop-' + ratio);

            document.querySelectorAll('[id^="btn-crop-"]').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById('btn-crop-' + ratio);
            if (btn) btn.classList.add('active');
        }}

        // 4. Columns Layout Controller
        function setCols(n) {{
            document.body.classList.remove('cols-5', 'cols-4', 'cols-3', 'cols-2');
            document.body.classList.add('cols-' + n);

            document.querySelectorAll('[id^="btn-cols-"]').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById('btn-cols-' + n);
            if (btn) btn.classList.add('active');
        }}

        // 5. Page Theme Controller
        function setTheme(theme) {{
            if (theme === 'light') {{
                document.body.classList.add('theme-light');
                document.getElementById('btn-theme-light').classList.add('active');
                document.getElementById('btn-theme-dark').classList.remove('active');
            }} else {{
                document.body.classList.remove('theme-light');
                document.getElementById('btn-theme-dark').classList.add('active');
                document.getElementById('btn-theme-light').classList.remove('active');
            }}
        }}

        // 6. Section 1 Method Column Filter
        function toggleMethod(methodId, visible) {{
            const elements = document.querySelectorAll('.col-' + methodId);
            elements.forEach(el => {{
                if (visible) el.classList.remove('hidden');
                else el.classList.add('hidden');
            }});
        }}

        // 7. Section 2 Live Tab Flip Mode
        function toggleStorefrontMode() {{
            isSfTabMode = !isSfTabMode;
            document.body.classList.toggle('sf-tab-mode', isSfTabMode);
            const btn = document.getElementById('btn-toggle-sf-mode');
            if (isSfTabMode) {{
                btn.innerHTML = '📜 Przełącz tryb: Wszystkie subsekcje pod sobą';
                selectSfTab('sf-sec-dat2');
            }} else {{
                btn.innerHTML = '🔄 Przełącz tryb: Zakładki w miejscu';
                document.querySelectorAll('.subnav-btn').forEach(b => b.classList.remove('active'));
            }}
        }}

        function selectSfTab(secId) {{
            if (!isSfTabMode) return;
            document.querySelectorAll('.sf-section-box').forEach(s => s.classList.remove('active-tab'));
            const activeSec = document.getElementById(secId);
            if (activeSec) activeSec.classList.add('active-tab');

            document.querySelectorAll('.subnav-btn').forEach(b => b.classList.remove('active'));
            const mapBtn = {{
                'sf-sec-orig': 'sbtn-orig',
                'sf-sec-lanczos': 'sbtn-lanczos',
                'sf-sec-realesrgan': 'sbtn-realesrgan',
                'sf-sec-ultra': 'sbtn-ultra',
                'sf-sec-dat2': 'sbtn-dat2'
            }};
            const bid = mapBtn[secId];
            if (bid && document.getElementById(bid)) document.getElementById(bid).classList.add('active');
            window.scrollTo({{ top: 120, behavior: 'instant' }});
        }}

        // 8. Modal Lightbox
        const methodPaths = {{
            'orig': (stem) => '../sample_images/' + stem + '.png',
            'lanczos': (stem) => 'bicubic/' + stem + '.webp',
            'realesrgan': (stem) => 'realesrgan_x4plus/' + stem + '.webp',
            'ultra': (stem) => 'ultrasharp_x4/' + stem + '.webp',
            'dat2': (stem) => 'realwebphoto_dat2/' + stem + '.webp'
        }};

        const methodNames = {{
            'orig': 'Oryginał (256×256 px - piksele w skali 1:1)',
            'lanczos': 'Lanczos + Unsharp (1024×1024 px - interpolacja)',
            'realesrgan': 'Real-ESRGAN x4plus (1024×1024 px - RRDBNet)',
            'ultra': '4x-UltraSharp (1024×1024 px - mikro-tekstury)',
            'dat2': '4xRealWebPhoto DAT-2 🏆 (1024×1024 px - Vision Transformer)'
        }};

        function openModal(stem, methodId, title) {{
            currentStem = stem;
            currentMethod = methodId;
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
            if (e.target.id === 'image-modal') closeModal();
        }}

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

    out_master = OUTPUTS_DIR / "master_comparison.html"
    with open(out_master, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Generated master comparison: {out_master}")

    # Also save as index.html so it serves as the default entry point
    out_index = OUTPUTS_DIR / "index.html"
    with open(out_index, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Updated default index: {out_index}")


if __name__ == "__main__":
    build_master()
