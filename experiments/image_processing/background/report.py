"""Render the background comparison as a self-contained HTML report."""

import base64
from html import escape
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


def outline_overlay(image, mask):
    foreground = (np.asarray(mask) >= 128).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    outline = cv2.morphologyEx(foreground, cv2.MORPH_GRADIENT, kernel)
    return Image.composite(
        Image.new("RGB", image.size, "#ff2473"),
        image,
        Image.fromarray(outline * 255),
    )


def image_tag(image, label):
    image.thumbnail((512, 512), Image.Resampling.LANCZOS)
    with BytesIO() as buffer:
        image.save(buffer, format="WEBP", lossless=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return (
        f'<figure><figcaption>{label}</figcaption>'
        f'<img loading="lazy" src="data:image/webp;base64,{encoded}" alt="{label}"></figure>'
    )


def render_card(product_id, image, variants):
    product = escape(product_id)
    columns = "".join(
        f'<div>{image_tag(result, label)}'
        f'{image_tag(outline_overlay(image, mask), f"Kontur {label}")}</div>'
        for label, mask, result in variants
    )
    return f'<article><h2>{product}</h2><div class="pair">{columns}</div></article>'


def write_report(output, rows):
    report = """<!doctype html>
<html lang="pl">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GrabCut, U²-Net Lite i BiRefNet Lite Matting</title>
<style>
body { margin: 24px; background: #f5f6f8; color: #202328; font: 16px system-ui, sans-serif }
main { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 650px), 1fr)); gap: 16px }
article { padding: 12px; background: white; border-radius: 8px }
h2 { margin: 0 0 8px; font-size: 16px }
.pair { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px }
figure { margin: 0 }
figure + figure { margin-top: 8px }
figcaption { margin-bottom: 4px }
img { display: block; width: 100%; height: auto }
</style>
<h1>GrabCut, U²-Net Lite i BiRefNet Lite Matting</h1>
<p>Różowa linia pokazuje granicę maski na zdjęciu wejściowym.</p>
<main>
""" + "\n".join(rows) + "\n</main>\n</html>\n"
    output.write_text(report, encoding="utf-8")
