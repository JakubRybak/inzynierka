"""Apply a tint to the background using a precomputed foreground mask."""

from PIL import Image, ImageChops


def tint_background(image: Image.Image, foreground: Image.Image, shade: str) -> Image.Image:
    tinted = ImageChops.multiply(image, Image.new("RGB", image.size, shade))
    return Image.composite(image, tinted, foreground)
