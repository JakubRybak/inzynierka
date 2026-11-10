"""Generate an e-commerce storefront gallery comparison HTML.

Displays all 15 sample products across 3 distinct sections:
1. Section 1: Original 256x256 images (current repo state)
2. Section 2: Method 1 - 4x-UltraSharp (1024x1024 WebP)
3. Section 3: Method 2 - 4xRealWebPhoto DAT-2 (1024x1024 WebP)

Includes a sticky header and a live in-place tab-switch mode to flip the whole store view instantly.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE_DIR = HERE / "sample_images"
OUTPUTS_DIR = HERE / "outputs"

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


def build_cards(images: list[Path], method_key: str) -> str:
    html = []
    for img_path in images:
        stem = img_path.stem
        parts = stem.split("_")
        pid = parts[-1]
        meta = METADATA.get(pid, {
            "brand": "FashionGen",
            "category": parts[1].capitalize(),
            "title": f"Product {pid}",
            "price": "$250"
        })

        if method_key == "original":
            img_src = f"../sample_images/{img_path.name}"
            res_label = "256 &times; 256 px"
            size_badge = "Oryginał"
        elif method_key == "ultrasharp":
            img_src = f"ultrasharp_x4/{stem}.webp"
            res_label = "1024 &times; 1024 px"
            size_badge = "4x-UltraSharp · WebP"
        elif method_key == "dat2":
            img_src = f"realwebphoto_dat2/{stem}.webp"
            res_label = "1024 &times; 1024 px"
            size_badge = "4xRealWebPhoto DAT-2 · WebP"
        else:
            img_src = f"bicubic/{stem}.webp"
            res_label = "1024 &times; 1024 px"
            size_badge = "Lanczos · WebP"

        card = f"""
        <div class="product-card" data-pid="{pid}">
            <div class="product-media">
                <span class="media-badge">{res_label}</span>
                <img src="{img_src}" alt="{meta['title']}" loading="lazy">
            </div>
            <div class="product-info">
                <div class="product-brand">{meta['brand']}</div>
                <div class="product-title">{meta['title']}</div>
                <div class="product-category">{meta['category']}</div>
                <div class="product-price">{meta['price']}</div>
            </div>
        </div>
        """
        html.append(card)
    return "\n".join(html)


def main():
    images = sorted(list(SAMPLE_DIR.glob("*.png")))
    if not images:
        raise RuntimeError(f"No sample images found in {SAMPLE_DIR}")

    cards_orig = build_cards(images, "original")
    cards_ultra = build_cards(images, "ultrasharp")
    cards_dat2 = build_cards(images, "dat2")

    html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Storefront: Zbiorcze porównanie jakości zdjęć</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-card: #131b2e;
            --border: #223049;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-orange: #fb923c;
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
            padding-bottom: 80px;
        }}

        /* Sticky top navigation */
        .topbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(9, 13, 22, 0.92);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .brand-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .brand-title span {{
            font-size: 12px;
            color: var(--accent-blue);
            font-weight: 500;
            background: rgba(56, 189, 248, 0.12);
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}

        .nav-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .nav-btn {{
            background: var(--bg-card);
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .nav-btn:hover {{
            background: #1e293b;
            color: #ffffff;
            border-color: var(--accent-blue);
        }}

        .nav-btn.active {{
            background: var(--accent-blue);
            color: #090d16;
            border-color: var(--accent-blue);
            font-weight: 700;
        }}

        .mode-toggle {{
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #475569;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            font-weight: 600;
        }}
        .mode-toggle:hover {{
            border-color: #94a3b8;
        }}

        .main-container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 24px;
        }}

        /* Section Header */
        .section-box {{
            margin-bottom: 60px;
            scroll-margin-top: 80px;
        }}

        .section-header {{
            background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .section-header.orig-header {{
            border-left: 5px solid var(--accent-orange);
        }}
        .section-header.ultra-header {{
            border-left: 5px solid var(--accent-blue);
        }}
        .section-header.dat2-header {{
            border-left: 5px solid var(--accent-green);
        }}

        .section-title-wrap h2 {{
            font-size: 20px;
            color: #ffffff;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-title-wrap p {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        .section-stats {{
            display: flex;
            gap: 16px;
            font-size: 12px;
        }}
        .stat-badge {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid #334155;
            padding: 6px 12px;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .stat-badge b {{
            color: #ffffff;
            font-size: 13px;
        }}

        /* Product Grid */
        .store-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 18px;
        }}

        @media (max-width: 1200px) {{
            .store-grid {{ grid-template-columns: repeat(4, 1fr); }}
        }}
        @media (max-width: 900px) {{
            .store-grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        @media (max-width: 600px) {{
            .store-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}

        .product-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }}

        .product-card:hover {{
            transform: translateY(-3px);
            border-color: #3b82f6;
            box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.5);
        }}

        .product-media {{
            position: relative;
            background: #090d16;
            aspect-ratio: 1 / 1;
            width: 100%;
            overflow: hidden;
        }}

        .product-media img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.3s ease;
        }}

        .orig-section .product-media img {{
            image-rendering: pixelated;
        }}

        .product-card:hover .product-media img {{
            transform: scale(1.05);
        }}

        .media-badge {{
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(9, 13, 22, 0.75);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #cbd5e1;
            font-size: 10px;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 500;
        }}

        .product-info {{
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            flex-grow: 1;
        }}

        .product-brand {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent-blue);
        }}

        .product-title {{
            font-size: 14px;
            font-weight: 600;
            color: #ffffff;
            line-height: 1.3;
        }}

        .product-category {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .product-price {{
            margin-top: 6px;
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
        }}

        /* In-place tab switcher styles */
        .tab-content {{
            display: block;
        }}
        body.tab-mode .section-box {{
            display: none;
            margin-bottom: 0;
        }}
        body.tab-mode .section-box.active-tab {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="brand-title">
            FASHION STORE <span>SUPER-RESOLUTION DEMO</span>
        </div>

        <div class="nav-buttons">
            <a href="#sec-orig" class="nav-btn" id="btn-orig" onclick="selectTab('sec-orig')">
                <b>1.</b> Oryginały (256px)
            </a>
            <a href="#sec-ultra" class="nav-btn" id="btn-ultra" onclick="selectTab('sec-ultra')">
                <b>2.</b> 4x-UltraSharp (1024px)
            </a>
            <a href="#sec-dat2" class="nav-btn" id="btn-dat2" onclick="selectTab('sec-dat2')">
                <b>3.</b> 4xRealWebPhoto DAT-2 (1024px)
            </a>
        </div>

        <div>
            <button class="mode-toggle" id="toggle-mode-btn" onclick="toggleViewMode()">
                🔄 Przełącz tryb: Zakładki w miejscu
            </button>
        </div>
    </div>

    <div class="main-container">

        <!-- ==================== SEKCJA 1: ORYGINAŁY ==================== -->
        <section class="section-box orig-section active-tab" id="sec-orig">
            <div class="section-header orig-header">
                <div class="section-title-wrap">
                    <h2>1. Zdjęcia oryginalne (Stan obecny w repozytorium)</h2>
                    <p>Rozdzielczość 256&times;256 px rozciągnięta w kartach produktów. Zwróć uwagę na efekt rozmycia, brak ostrości materiałów i niewyraźne napisy/detale.</p>
                </div>
                <div class="section-stats">
                    <div class="stat-badge">
                        <span>Rozdzielczość:</span>
                        <b>256 &times; 256 px</b>
                    </div>
                    <div class="stat-badge">
                        <span>Średni rozmiar pliku:</span>
                        <b>~45 KB (PNG)</b>
                    </div>
                    <div class="stat-badge">
                        <span>Jakość wizualna:</span>
                        <b style="color: var(--accent-orange)">Niska (rozmyta)</b>
                    </div>
                </div>
            </div>

            <div class="store-grid">
                {cards_orig}
            </div>
        </section>

        <!-- ==================== SEKCJA 2: 4x-ULTRASHARP ==================== -->
        <section class="section-box ultra-section" id="sec-ultra">
            <div class="section-header ultra-header">
                <div class="section-title-wrap">
                    <h2>2. Metoda 1: 4x-UltraSharp (ESRGAN)</h2>
                    <p>Skalowanie 4x modelem ESRGAN dostrojonym pod kątem mikro-tekstur. Wyraźne, twarde krawędzie, guziki i zamki. Najszybsza z metod neuronowych.</p>
                </div>
                <div class="section-stats">
                    <div class="stat-badge">
                        <span>Rozdzielczość wyjściowa:</span>
                        <b>1024 &times; 1024 px</b>
                    </div>
                    <div class="stat-badge">
                        <span>Czas / zdjęcie (M1 Pro):</span>
                        <b>681 ms</b>
                    </div>
                    <div class="stat-badge">
                        <span>Czas dla 10 000 produktów:</span>
                        <b style="color: var(--accent-blue)">1h 53m (Szybki)</b>
                    </div>
                    <div class="stat-badge">
                        <span>Średni rozmiar WebP:</span>
                        <b>46.8 KB</b>
                    </div>
                </div>
            </div>

            <div class="store-grid">
                {cards_ultra}
            </div>
        </section>

        <!-- ==================== SEKCJA 3: 4xREALWEBPHOTO (DAT-2) ==================== -->
        <section class="section-box dat2-section" id="sec-dat2">
            <div class="section-header dat2-header">
                <div class="section-title-wrap">
                    <h2>3. Metoda 2: 4xRealWebPhoto (DAT-2 Transformer) 🏆</h2>
                    <p>Skalowanie 4x architekturą Dual Aggregation Transformer (2024/2025). Naturalne sploty wełny i tkanin, płynne przejścia tonalne, naturalna skóra, zero plastiku.</p>
                </div>
                <div class="section-stats">
                    <div class="stat-badge">
                        <span>Rozdzielczość wyjściowa:</span>
                        <b>1024 &times; 1024 px</b>
                    </div>
                    <div class="stat-badge">
                        <span>Czas / zdjęcie (M1 Pro):</span>
                        <b>3 157 ms (3.1s)</b>
                    </div>
                    <div class="stat-badge">
                        <span>Czas dla 10 000 produktów:</span>
                        <b style="color: var(--accent-green)">8h 46m (Najwyższa jakość)</b>
                    </div>
                    <div class="stat-badge">
                        <span>Średni rozmiar WebP:</span>
                        <b>41.7 KB</b>
                    </div>
                </div>
            </div>

            <div class="store-grid">
                {cards_dat2}
            </div>
        </section>

    </div>

    <script>
        let isTabMode = false;

        function toggleViewMode() {{
            isTabMode = !isTabMode;
            document.body.classList.toggle('tab-mode', isTabMode);
            const btn = document.getElementById('toggle-mode-btn');
            if (isTabMode) {{
                btn.innerHTML = '📜 Przełącz tryb: Sekcje jedna pod drugą';
                selectTab('sec-dat2');
            }} else {{
                btn.innerHTML = '🔄 Przełącz tryb: Zakładki w miejscu';
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            }}
        }}

        function selectTab(secId) {{
            if (!isTabMode) {{
                return; // Normal anchor scrolling
            }}
            document.querySelectorAll('.section-box').forEach(s => s.classList.remove('active-tab'));
            document.getElementById(secId).classList.add('active-tab');

            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            if (secId === 'sec-orig') document.getElementById('btn-orig').classList.add('active');
            if (secId === 'sec-ultra') document.getElementById('btn-ultra').classList.add('active');
            if (secId === 'sec-dat2') document.getElementById('btn-dat2').classList.add('active');

            window.scrollTo({{ top: 0, behavior: 'instant' }});
        }}
    </script>
</body>
</html>
"""

    out_file = OUTPUTS_DIR / "storefront_comparison.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Generated storefront gallery comparison: {out_file}")


if __name__ == "__main__":
    main()
