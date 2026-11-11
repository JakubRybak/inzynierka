"""
Extracted features of a product as a short English text for an embedding, e.g. "Classic Coats. For women. Green.
55% polyester, 45% cotton. Zip closure. Parka. Stand collar. Oversized fit. With hood. Uninsulated. Short length."
A value that names itself (with hood, long sleeve, stand collar) is written alone, other values get the noun of their
feature (midi length, oversized fit). Other, Not Applicable and Unknown are left out.
"""
HIDDEN = {"Other", "Not Applicable", "Unknown"}
FIRST = ["gender", "colors", "main_composition", "lining_composition"]
TEMPLATE = {"fit": "{} fit", "length": "{} length", "pattern": "{} pattern", "dress_silhouette": "{} silhouette",
            "skirt_silhouette": "{} silhouette", "skirt_type": "{} skirt", "shorts_type": "{} shorts",
            "jacket_style": "{} jacket", "leg_shape": "{} leg", "waistband_type": "{} waistband",
            "strap_width": "{} straps", "closure_type": "{} closure", "dress_type": "{} dress",
            "neckline": "{} neckline", "insulation": "{} insulation"}
SELF = {"Full-Length", "Mid-Length", "Animal Print", "Wide-Leg", "Sweatshorts", "Open Front", "Pullover", "Belted",
        "Double-Breasted", "Shirt Dress", "Sweater Dress", "Sweatshirt Dress", "T-Shirt Dress", "Crewneck", "High Neck", "Scoop Neck",
        "V-Neck", "Fleece Lined", "Shearling Lined", "Synthetic Padding", "Uninsulated"}
VALUE = {("gender", "Women"): "for women", ("gender", "Men"): "for men", ("distressing", "Clean"): "no distressing",
         ("strap_style", "Standard"): "standard straps", ("strap_style", "Standard Sleeved"): "sleeved",
         ("strap_style", "Halter"): "halter neck", ("coat_style", "Standard"): None}


def composition(shares, lining=False):
    if set(shares) == {"Unlined"}:
        return "unlined"
    text = ", ".join(f"{s:g}% {m.lower()}" for m, s in sorted(shares.items(), key=lambda kv: -kv[1]) if s > 0)
    return f"lined with {text}" if lining else text


def value_text(feature, value):
    if (feature, value) in VALUE:
        return VALUE[feature, value]
    if value in SELF or feature not in TEMPLATE:
        return value.lower()
    return TEMPLATE[feature].format(value.lower())


def feature_text(p):
    parts = [p["category"]]
    f = p["features"]
    for name in sorted(f, key=lambda k: (FIRST.index(k) if k in FIRST else len(FIRST), k)):
        v = f[name]
        if isinstance(v, dict):
            text = composition(v, lining=name == "lining_composition")
        elif isinstance(v, list):
            values = [x for x in v if x not in HIDDEN]
            text = (" and ".join(x.lower() for x in values) if name == "colors"
                    else ", ".join(filter(None, (value_text(name, x) for x in values))))
        elif v is None or v in HIDDEN:
            continue
        else:
            text = value_text(name, str(v))
        if text:
            parts.append(text[0].upper() + text[1:])
    return ". ".join(parts) + "."
