"""
Colour signal of the phrase bank. Every product has one to three colours with a share (ranking_data/
product_colors.parquet, from offline/product_colors.py), and the colour dictionary (ranking_data/color_names.parquet)
gives the typical hex of every colour name the products got. A shade phrase gets a target: a colour name of the
dictionary (exactly, or the nearest one by embedding when the similarity reaches MATCH) or a bank shade with its hex,
or only a lighter or darker direction. A phrase that asks only for lightness ("light coloured", "dark") is about as
close to many colour names of different hues ("light grey", "light pink", "light blue"): when the names within
HUE_MARGIN of the nearest one spread over the hue circle (HUE_SPREAD) and are not just greys, it gets the direction
of their mean lightness instead of one of them. Two general entries do the same for phrases nearer to them than to
any colour name, within GENERIC_TOLERANCE ("light coloured", "w jasnym kolorze", "dark coloured"). A candidate
scores by how close its colours are to the target in CIELAB, weighted by their share.
"""
import numpy as np
import pandas as pd

import common

PRODUCTS = common.SEARCH_UI / "ranking_data/product_colors.parquet"
NAMES = common.SEARCH_UI / "ranking_data/color_names.parquet"
VECTORS = "color_embeddings.npz"
MATCH = 0.80  # chosen on the phrase bank: 83% of its shade phrases and 1.8% of the other phrases reach it
SIGMA = 20.0  # CIELAB distance at which a colour still counts as about 60% the same
# chosen on the phrase bank: "dark", "jasny", "pastel" and "neon" spread at least this much, 1 of its 71 shades with
# a hue too ("pastel blue"), besides greys
HUE_MARGIN, HUE_SPREAD, MIN_CHROMA = 0.02, 0.25, 10.0
GENERIC = {"light colour": "light", "dark colour": "dark"}
# chosen on test phrases and the phrase bank: "light coloured" is 0.88 to "light colour" and 0.90 to "light beige";
# with 0.03 no bank shade with a hue goes to a general entry
GENERIC_TOLERANCE = 0.03
SLOTS = 3


def lab(hex_value):
    """CIELAB (L*, a*, b*) of an sRGB hex colour, D65."""
    rgb = np.array([int(hex_value[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    rgb = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ rgb
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def embed_names(names, embed, folder):
    """Embeddings of the colour names and the GENERIC entries (query format) in folder/VECTORS; only new names are
    embedded."""
    names = list(names) + [g for g in GENERIC if g not in names]
    return common.embed_texts(names, [common.query_text(n) for n in names], embed, folder / VECTORS)


class Colours:
    def __init__(self, products, frame, names, vectors, generic_vectors=None):
        index = {p["product_id"]: i for i, p in enumerate(products)}
        self.lab = np.zeros((len(products), SLOTS, 3))
        self.share = np.zeros((len(products), SLOTS))
        self.family = np.full((len(products), SLOTS), "", dtype=object)
        for r in frame.itertuples():
            i = index.get(r.product_id)
            if i is not None and r.rank < SLOTS:
                self.lab[i, r.rank], self.share[i, r.rank], self.family[i, r.rank] = lab(r.hex), r.share, r.family
        self.names = list(names["name"])
        self.hex = dict(zip(names["name"], names["hex"]))
        self.families = dict(zip(names["name"], names["family"]))
        self.E = common.normalize(np.asarray(vectors, np.float32))
        points = np.stack([lab(h) for h in names["hex"]]) if len(names) else np.zeros((0, 3))
        self.L, self.chroma = points[:, 0], np.hypot(points[:, 1], points[:, 2])
        self.hue = np.exp(1j * np.arctan2(points[:, 2], points[:, 1]))
        self.G = common.normalize(np.asarray(generic_vectors, np.float32)) if generic_vectors is not None else None

    def lightness_only(self, near):
        """"light" or "dark" when the names near spread over the hue circle and are not just greys, else None."""
        w = self.chroma[near]
        if len(near) < 2 or w.mean() < MIN_CHROMA:
            return None
        spread = 1 - abs((w * self.hue[near]).sum()) / w.sum()
        if spread < HUE_SPREAD:
            return None
        return "light" if self.L[near].mean() >= 50 else "dark"

    def target(self, text, vector=None):
        """The colour of a dictionary name, exactly or the nearest one; None when nothing reaches MATCH."""
        if text in self.hex:
            return dict(name=text, hex=self.hex[text], family=self.families[text], similarity=1.0)
        if vector is None:
            return None
        sims = self.E @ vector
        j = int(np.argmax(sims))
        if self.G is not None:
            general = self.G @ vector
            g = int(np.argmax(general))
            if general[g] >= MATCH and general[g] >= sims[j] - GENERIC_TOLERANCE:
                lightness = list(GENERIC.values())[g]
                return dict(name=f"{lightness} shades", lightness=lightness, family=None,
                            similarity=round(float(general[g]), 3))
        if sims[j] < MATCH:
            return None
        lightness = self.lightness_only(np.flatnonzero(sims >= sims[j] - HUE_MARGIN))
        if lightness:
            return dict(name=f"{lightness} shades", lightness=lightness, family=None, similarity=round(float(sims[j]), 3))
        name = self.names[j]
        return dict(name=name, hex=self.hex[name], family=self.families[name], similarity=round(float(sims[j]), 3))

    def score(self, target, cand):
        """With a hex: sum over the candidate's colours of share × exp(-distance² / 2 SIGMA²). With only a lightness:
        the share-weighted L* of the candidate's colours of the target family (or of all its colours), negated for
        "dark"."""
        points, share = self.lab[cand], self.share[cand]
        if target.get("hex"):
            d2 = ((points - lab(target["hex"])) ** 2).sum(axis=-1)
            return (share * np.exp(-d2 / (2 * SIGMA ** 2))).sum(axis=1)
        w = share * (self.family[cand] == target["family"]) if target.get("family") else share
        w = np.where(w.sum(axis=1, keepdims=True) > 0, w, share)
        lightness = (w * points[..., 0]).sum(axis=1) / np.maximum(w.sum(axis=1), 1e-9)
        return -lightness if target.get("lightness") == "dark" else lightness


def load(products, folder=common.DATA):
    """Colours of the products, or None when the colour files or the name embeddings (prepare.py) are missing."""
    if not (PRODUCTS.exists() and NAMES.exists() and (folder / VECTORS).exists()):
        return None
    names = pd.read_parquet(NAMES)
    stored = np.load(folder / VECTORS)
    known = dict(zip(stored["ids"].tolist(), stored["vectors"]))
    if not all(n in known for n in list(names["name"]) + list(GENERIC)):
        return None
    return Colours(products, pd.read_parquet(PRODUCTS), names, np.stack([known[n] for n in names["name"]]),
                   np.stack([known[g] for g in GENERIC]))
