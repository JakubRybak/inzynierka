"""Render a self-contained report with one row per product."""

import base64
from html import escape
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


def render_row(product_id, variants):
    figures = []
    for label, image in variants:
        preview = ImageOps.fit(image, (270, 450), Image.Resampling.LANCZOS)
        with BytesIO() as buffer:
            preview.save(buffer, format="WEBP", quality=90)
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        label = escape(label)
        figures.append(
            f'<figure><figcaption>{label}</figcaption>'
            f'<img src="data:image/webp;base64,{encoded}" loading="lazy" '
            f'width="270" height="450" alt="{label}"></figure>'
        )
    return f'<article><h2>{escape(product_id)}</h2><div class="variants">{"".join(figures)}</div></article>'


def write_report(output: Path, rows: list[str], columns: int) -> None:
    heading = """<!doctype html>
<html lang="pl">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Odcienie szarego tła</title>
<style>
* { box-sizing: border-box }
body { max-width: 1440px; margin: auto; padding: 24px; background: #f5f6f8; color: #202328; font: 16px system-ui, sans-serif }
h1 { margin: 0 }
p { margin: 8px 0 24px; color: #4a4f59 }
article { padding: 14px; margin-bottom: 12px; background: white; border-radius: 8px; overflow-x: auto }
h2 { font-size: 16px; margin: 0 0 8px }
.variants { display: grid; grid-template-columns: repeat(var(--columns), minmax(105px, 1fr)); gap: 10px }
figure { margin: 0 }
figcaption { font-size: 14px; margin-bottom: 6px }
img { display: block; width: 100%; height: auto; border-radius: 4px }
</style>
<h1>Odcienie szarego tła</h1>
<p>Te same zdjęcia w kadrze 3:5. Szarość jest nakładana na tło za pomocą gotowej maski BiRefNet.</p>
"""
    output.write_text(
        heading + f'<main style="--columns: {columns}">\n' + "\n".join(rows) + "\n</main>\n</html>\n",
        encoding="utf-8",
    )
