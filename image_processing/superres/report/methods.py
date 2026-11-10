"""Display metadata and benchmark results for every method shown in the report.

Timings were measured on Apple Silicon M1 Pro (PyTorch MPS) for 256x256 -> 1024x1024.
"""

from dataclasses import dataclass, field

ORIGINAL_ID = "original"
DEFAULT_PREVIEW_ID = "dat2"


@dataclass(frozen=True)
class MethodInfo:
    id: str
    name: str
    short_name: str            # used in modal tabs and storefront navigation
    tag: str
    family: str
    year: str
    source: str
    time_per_image: str
    time_per_10k: str
    fidelity: float            # garment fidelity score, 0-10
    realism: float             # micro-texture realism score, 0-10
    hallucination_risk: str
    memory: str
    color: str
    description: str
    pros: str
    cons: str
    highlight: str = ""        # benchmark table row style: "winner" | "hybrid" | "generative"
    tab_style: str = ""        # active modal tab style: "winner" | "hybrid" | "generative" | "diffusion"

    @property
    def is_original(self) -> bool:
        return self.id == ORIGINAL_ID

    @property
    def resolution(self) -> int:
        return 256 if self.is_original else 1024

    @property
    def file_format(self) -> str:
        return "png" if self.is_original else "webp"

    @property
    def hallucination_level(self) -> str:
        """CSS modifier for the hallucination risk colour."""
        if self.hallucination_risk.startswith("Średnie"):
            return "high"
        if self.hallucination_risk.startswith("Niskie"):
            return "low"
        return "none"


@dataclass(frozen=True)
class ColumnFilter:
    id: str
    label: str
    method_ids: tuple[str, ...] = field(default=())   # empty = show all


METHODS: list[MethodInfo] = [
    MethodInfo(
        id=ORIGINAL_ID,
        name="Oryginał (Stan obecny)",
        short_name="Oryginał (256px)",
        tag="WEJŚCIE 256×256",
        family="Raw Input",
        year="FashionGen",
        source="Dataset",
        time_per_image="0 ms",
        time_per_10k="0 min",
        fidelity=10.0,
        realism=4.0,
        hallucination_risk="Brak (0%)",
        memory="0 GB",
        color="#fb923c",
        description="Oryginalny plik 256×256 px powiększony rozdzielczością ekranu.",
        pros="Stan wyjściowy bazy FashionGen.",
        cons="Mocno rozmyte, pikseloza na ekranach Retina/HiDPI.",
    ),
    MethodInfo(
        id="lanczos",
        name="Lanczos + Unsharp",
        short_name="Lanczos",
        tag="BASELINE MATEMATYCZNY",
        family="Classical Filter",
        year="Standard",
        source="Non-AI Filter",
        time_per_image="27.8 ms",
        time_per_10k="4.6 min",
        fidelity=7.0,
        realism=5.5,
        hallucination_risk="Brak (0%)",
        memory="< 0.1 GB",
        color="#94a3b8",
        description="Interpolacja matematyczna sinc z wyostrzeniem unsharp mask. Zero wag neuronowych.",
        pros="Błyskawiczny (36 FPS na CPU).",
        cons="Rozmycie, brak rekonstrukcji jakichkolwiek nowych detali tkanin.",
    ),
    MethodInfo(
        id="realesrgan",
        name="Real-ESRGAN x4plus",
        short_name="Real-ESRGAN",
        tag="KLASYCZNY CNN",
        family="ESRGAN / RRDBNet",
        year="2021",
        source="ICCV 2021",
        time_per_image="688.3 ms",
        time_per_10k="1.91 h",
        fidelity=8.5,
        realism=7.8,
        hallucination_risk="Brak (0%)",
        memory="~1.5 GB",
        color="#c084fc",
        description="Przemysłowy standard CNN poprzednich lat. Skutecznie usuwa kompresję JPEG, ale mocno wygładza fakturę tkanin.",
        pros="Brak artefaktów szumu, stabilny, szybki.",
        cons="Zbyt woskowaty wygląd w zbliżeniu na dzianinach i wełnie.",
    ),
    MethodInfo(
        id="ultrasharp",
        name="4x-UltraSharp",
        short_name="4x-UltraSharp",
        tag="CNN MIKRO-FAKTURY",
        family="ESRGAN Fine-Tuned",
        year="2023",
        source="Community SOTA",
        time_per_image="680.7 ms",
        time_per_10k="1.89 h",
        fidelity=8.8,
        realism=8.1,
        hallucination_risk="Brak (0%)",
        memory="~1.5 GB",
        color="#38bdf8",
        description="Wyostrzony model ESRGAN do fotografii. Bardzo ostry obrys, ale może dawać lekko twardy, cyfrowy obrys na zagięciach.",
        pros="Ekspresowy (680 ms, poniżej 2h na 10 000 produktów).",
        cons="Twardsze, bardziej plastikowe przejścia tonalne niż w modelach nowej generacji.",
    ),
    MethodInfo(
        id="dat2",
        name="4xRealWebPhoto DAT-2 🏆",
        short_name="DAT-2 🏆",
        tag="LIDER BENCHMARKU",
        family="Vision Transformer",
        year="2024",
        source="SOTA Real-World SR",
        time_per_image="3.16 s",
        time_per_10k="8.8 h",
        fidelity=9.6,
        realism=8.6,
        hallucination_risk="Brak (0%)",
        memory="~2.4 GB",
        color="#34d399",
        description="Dual Aggregation Transformer. Wybitne zbalansowanie ostrości, miękkich zagnieceń i wierności bez zniekształceń. Jeden krok regresyjny.",
        pros="100% wierność krojom i kolorom, brak zniekształceń guzików/szwów, mieści się w 8.8h dla 10k ujęć.",
        cons="Dla twarzy modeli w kadrze nie syntetyzuje mikroskopijnych detali rzęs i tęczówek.",
        highlight="winner",
        tab_style="winner",
    ),
    MethodInfo(
        id="dat2_gfpgan",
        name="DAT-2 + GFPGAN 👔✨",
        short_name="DAT-2 + GFPGAN 👔✨",
        tag="HYBRYDA E-COMMERCE",
        family="Transformer + Face GAN",
        year="2024",
        source="DAT-2 + GFPGAN v1.4",
        time_per_image="3.77 s",
        time_per_10k="10.5 h",
        fidelity=9.6,
        realism=9.8,
        hallucination_risk="Brak (0%)",
        memory="~2.8 GB",
        color="#a855f7",
        description="Najwyższy standard produkcyjny dla sklepów modowych. Tkanina i krój ubrania są odtwarzane przez bezbłędny DAT-2 (zero halucynacji materiału), a twarze modeli, oczy, zęby i włosy są wykrywane przez RetinaFace i fotorealistycznie rekonstruowane przez model GFPGAN.",
        pros="Idealna harmonia: 100% wierności faktury odzieży + ostra, naturalna twarz i spojrzenie modela. Zero zniekształceń kroju.",
        cons="Dwuetapowy potok inferencyjny (detekcja, odnowa twarzy i fuzja masek w czasie +0.6s/zdjęcie).",
        highlight="hybrid",
        tab_style="hybrid",
    ),
    MethodInfo(
        id="aurasr",
        name="AuraSR-v2 (GigaGAN 2025) ⚡",
        short_name="AuraSR-v2 ⚡",
        tag="GENERATYWNY GigaGAN",
        family="Generative GigaGAN",
        year="2024/2025",
        source="fal.ai / Aleph Alpha",
        time_per_image="12.84 s",
        time_per_10k="35.7 h",
        fidelity=9.1,
        realism=9.6,
        hallucination_risk="Niskie (< 5%)",
        memory="~3.8 GB",
        color="#f43f5e",
        description="Jednokrokowy generatywny upscaler GigaGAN od fal.ai. Dorysowuje autentyczne mikroskopijne sploty nitek, mikro-cienie i naturalną fakturę bez rozmyć (tryb overlapped przeciw szwom).",
        pros="Fotorealistyczna, ostra mikro-struktura materiałów niemożliwa do uzyskania klasycznymi filtrami.",
        cons="Dłuższy czas inferencji (~12.8s na Apple Silicon MPS), lekka tendencja do wyostrzania szumów z kompresji.",
        highlight="generative",
        tab_style="generative",
    ),
    MethodInfo(
        id="sd_x4",
        name="Stable Diffusion x4 🌪️",
        short_name="SD x4 🌪️",
        tag="LATENT DIFFUSION",
        family="Diffusion Model",
        year="2023/2024",
        source="Stability AI Official",
        time_per_image="24.50 s",
        time_per_10k="68.1 h",
        fidelity=8.4,
        realism=9.4,
        hallucination_risk="Średnie (~15%)",
        memory="~3.5 GB",
        color="#06b6d4",
        description="Klasyczna, pełna dyfuzja wielokrokowa (12 kroków odszumiania VAE) od Stability AI. Działa w przestrzeni cech ukrytych sterowana wektorami tekstowymi promptu e-commerce.",
        pros="Czysty proces dyfuzyjny, doskonała głębia plastyczna, miękkie studyjne oświetlenie i redukcja szumów.",
        cons="Najdłuższy czas przetwarzania (24.5s), ryzyko drobnych halucynacji krojów guzików i lamówek.",
        highlight="generative",
        tab_style="diffusion",
    ),
]

COLUMN_FILTERS: list[ColumnFilter] = [
    ColumnFilter("all", "🌟 Wszystkie 8 metod"),
    ColumnFilter("top", "🏆 Liderzy Jakości (DAT-2, Hybryda GFPGAN, AuraSR-v2)",
                 (ORIGINAL_ID, "dat2", "dat2_gfpgan", "aurasr")),
    ColumnFilter("generative", "✨ Generatywne & Dyfuzja (AuraSR-v2, SD x4, DAT-2+GFPGAN)",
                 (ORIGINAL_ID, "dat2", "dat2_gfpgan", "aurasr", "sd_x4")),
    ColumnFilter("classic", "📐 Klasyczne & CNN (Oryginał, Lanczos, Real-ESRGAN, UltraSharp)",
                 (ORIGINAL_ID, "lanczos", "realesrgan", "ultrasharp")),
]
