"""Catalog metadata for the FashionGen sample products shown in the report."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Product:
    brand: str
    category: str
    title: str
    price: str
    material: str


@dataclass(frozen=True)
class SampleImage:
    """One input photo together with its product metadata.

    Filenames follow `<index>_<category>_<product_id>.png`, e.g. `01_jacket_86605.png`.
    """

    path: Path
    product_id: str
    product: Product

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def display_name(self) -> str:
        return f"{self.product.brand} — {self.product.title}"


PRODUCTS: dict[str, Product] = {
    "86605": Product("Diesel", "Jackets", "Leather Biker Jacket", "$335", "Naturalna skóra licowa, metalowy zamek błyskawiczny, napy na kołnierzu"),
    "86933": Product("Thom Browne", "Knit Sweaters", "Wool Knit Sweater", "$970", "Ciężka wełna dziewicza o grubym splocie warkoczowym, ściągacze"),
    "87389": Product("Givenchy", "T-shirts", "Graphic Print T-Shirt", "$970", "Cienka bawełna czesana, sitodruk graficzny, mikro-szwy"),
    "86877": Product("Rag & Bone", "Dresses", "Silk Sleeveless Dress", "$595", "Gładki jedwab krepowy, subtelny połysk, lejące drapowanie"),
    "86779": Product("Dsquared2", "Shirts", "Tailored Check Shirt", "$645", "Bawełniana popelina w kratę, guziki z masy perłowej, kołnierzyk włoski"),
    "86773": Product("Dsquared2", "Jeans", "Distressed Denim Jeans", "$630", "Denim bawełniany 12oz, przetarcia i zaciągnięcia, żółte stebnowanie"),
    "99750": Product("Comme des Garçons", "Classic Coats", "Classic Wool Coat", "$2,615", "Wełniane sukno płaszczowe, głęboka matowa czerń, szerokie klapy"),
    "88112": Product("MM6 Maison Margiela", "Hoodies & Zipups", "Oversized Cotton Hoodie", "$385", "Dzianina dresowa french terry, sznurki z metalowymi skuwkami"),
    "91440": Product("MSGM", "Sweatshirts", "Crewneck Fleece Sweatshirt", "$245", "Czesany polar bawełniany, ściągacze ze spandexem"),
    "87053": Product("Lanvin", "Bombers", "Satin Bomber Jacket", "$1,595", "Włoski atłas satynowy, dwukierunkowy zamek riri, ściągacze w paski"),
    "86810": Product("Dsquared2", "Trousers", "Tailored Slim Trousers", "$495", "Wełna garniturowa z elastanem, zaprasowany kant, kieszenie cięte"),
    "89767": Product("Carven", "Skirts", "Pleated A-Line Skirt", "$530", "Plisowana tkanina poliestrowo-wełniana, ostre zaprasowania plis"),
    "90103": Product("D.Gnak by Kang.D", "Cardigans", "Draped Open Cardigan", "$455", "Miękka dzianina wiskozowa o asymetrycznym kroju, surowe wykończenie"),
    "87937": Product("T by Alexander Wang", "Blouses", "Silk V-Neck Blouse", "$225", "Krepa jedwabna o matowej strukturze, głęboki dekolt V"),
    "87953": Product("Band of Outsiders", "Polos", "Pique Cotton Polo Shirt", "$145", "Klasyczna bawełniana dzianina pika (wafelek), kołnierzyk ze splotem żebrowym"),
}


def load_sample_images(paths: list[Path]) -> list[SampleImage]:
    samples = []
    for path in paths:
        parts = path.stem.split("_")
        product_id = parts[-1]
        product = PRODUCTS.get(product_id) or Product(
            brand="FashionGen",
            category=parts[1].capitalize() if len(parts) > 2 else "Unknown",
            title=f"Product {product_id}",
            price="—",
            material="Brak opisu materiału",
        )
        samples.append(SampleImage(path, product_id, product))
    return samples
