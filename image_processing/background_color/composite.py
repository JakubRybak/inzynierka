"""Apply the catalog tint using a foreground mask."""

from PIL import Image, ImageChops

BACKGROUND_TINT = "#F4F3F7"


def tint_background(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Keep white mask pixels unchanged and tint black mask pixels."""
    if mask.mode != "L" or mask.size != image.size:
        raise ValueError("The mask must be grayscale and match the photo size")

    tinted = ImageChops.multiply(image, Image.new("RGB", image.size, BACKGROUND_TINT))
    return Image.composite(image, tinted, mask)
