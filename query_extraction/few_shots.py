"""Per-category few-shot examples for query extraction (Step 1 Category, Step 2a Full, Step 2b.1 Jev Features, Step 2b.2 Auxiliary).

Every category in the 22-category catalog has its own dedicated set of few-shot examples
strictly within that category. All examples are verified to have zero overlap with the
1,535 benchmark queries in query_extraction/benchmarks/queries.jsonl.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

CATEGORY_FEW_SHOTS: List[Dict[str, str]] = [
    {"query": "a green jersey T-shirt dress for summer", "answer": "Dresses"},
    {"query": "a ribbed singlet in white", "answer": "Tank tops & Camisoles"},
    {"query": "a black crop top for a party", "answer": "Tank tops & Camisoles"},
    {"query": "a cotton tee with a collar", "answer": "Polos"},
    {"query": "a tee to wear with a leather jacket", "answer": "T-shirts"},
    {"query": "a classic white dress shirt for office", "answer": "Shirts"},
    {"query": "a silk peasant blouse", "answer": "Blouses"},
    {"query": "a fleece crewneck sweatshirt without hood", "answer": "Sweatshirts"},
    {"query": "a grey zip-up hoodie", "answer": "Hoodies & Zipups"},
    {"query": "a cotton half-zip pullover with a hood", "answer": "Hoodies & Zipups"},
    {"query": "a chunky cable-knit wool jumper", "answer": "Knit Sweaters"},
    {"query": "an open-front knit cardigan", "answer": "Cardigans"},
    {"query": "a double-breasted wool peacoat", "answer": "Classic Coats"},
    {"query": "a beige belted gabardine trench", "answer": "Trench Coats"},
    {"query": "a black leather biker jacket", "answer": "Jackets"},
    {"query": "an olive nylon flight bomber", "answer": "Bombers"},
    {"query": "a quilted down gilet", "answer": "Vests"},
    {"query": "tailored high-waisted wool slacks", "answer": "Trousers"},
    {"query": "olive combat pants with utility cargo pockets", "answer": "Cargo Pants"},
    {"query": "grey fleece tapered joggers", "answer": "Sweatpants & Lounge Pants"},
    {"query": "faded bootcut denim jeans", "answer": "Jeans"},
    {"query": "men's linen bermuda shorts", "answer": "Shorts"},
    {"query": "a pleated midi skirt", "answer": "Skirts"},
    {"query": "a long-sleeve snap-crotch bodysuit", "answer": "Bodysuits"},
    {"query": "leather Chelsea ankle boots", "answer": "outside"},
    {"query": "something warm in black under 100 dollars", "answer": "outside"},
    {"query": "a cotton T-shirt or a linen dress", "answer": "outside"},
]


PER_CATEGORY_FEW_SHOTS: Dict[str, List[Dict[str, Any]]] = {
    "T-shirts": [
        {
            "query": "women’s turquoise Nike T-shirt, cotton without polyester, between 50 and 100 PLN, for hiking",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Cotton"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "gte", "value": 50},
                    {"feature": "price", "operator": "lte", "value": 100},
                ],
                "residual": ["turquoise", "for hiking"],
            },
            "note": "Shade 'turquoise' maps to Blue AND stays in residual; range uses gte + lte.",
        },
        {
            "query": "slim or regular T-shirt, but not oversized, around $30",
            "output": {
                "filters": [
                    {"feature": "fit", "operator": "in", "values": ["Slim", "Regular"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                    {"feature": "price", "operator": "around", "value": 30},
                ],
                "residual": [],
            },
            "note": "Positive and negative clauses on a single-choice feature are separate filters.",
        },
        {
            "query": "100% cotton all-black longline V-neck tee with long sleeves",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "length", "operator": "in", "values": ["Longline"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Long Sleeve"]},
                ],
                "residual": [],
            },
            "note": "'100% cotton' and 'all-black' both require equals_set (EXACT).",
        },
        {
            "query": "black and white striped cropped T-shirt, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Color conjunction uses contains_all (ALL); excluded shade 'not emerald' stays only in residual.",
        },
        {
            "query": "2x men's burgundy turtleneck T-shirt by Adidas up to 140 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "neckline", "operator": "in", "values": ["High Neck"]},
                    {"feature": "brand", "operator": "in", "values": ["Adidas"]},
                    {"feature": "price", "operator": "lte", "value": 140},
                ],
                "residual": ["2x", "burgundy", "turtleneck"],
            },
            "note": "'2x' is a size/pack (not price); 'burgundy' and 'turtleneck' map to Red/High Neck and stay in residual.",
        },
    ],
    "Polos": [
        {
            "query": "men's navy Lacoste polo shirt in 100% cotton under 250 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "brand", "operator": "in", "values": ["Lacoste"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "price", "operator": "lte", "value": 250},
                ],
                "residual": ["navy"],
            },
            "note": "'navy' maps to Blue and stays in residual; '100% cotton' maps to equals_set.",
        },
        {
            "query": "slim fit striped polo with long sleeves, cotton and elastane without polyester",
            "output": {
                "filters": [
                    {"feature": "fit", "operator": "in", "values": ["Slim"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Long Sleeve"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                ],
                "residual": [],
            },
            "note": "Combined materials use contains_all; excluded material uses contains_none.",
        },
        {
            "query": "women's sleeveless golf polo around $65, not oversized",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Sleeveless"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                    {"feature": "price", "operator": "around", "value": 65},
                ],
                "residual": ["golf"],
            },
            "note": "Activity/sport 'golf' stays in residual.",
        },
        {
            "query": "white and green polo shirt, but not turquoise, at least 80 EUR",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Green", "White"]},
                    {"feature": "price", "operator": "gte", "value": 80},
                ],
                "residual": ["not turquoise"],
            },
            "note": "Two joined colors use contains_all; excluded shade stays in residual.",
        },
        {
            "query": "all-white piqué polo by Ralph Lauren for work",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["White"]},
                    {"feature": "brand", "operator": "in", "values": ["Ralph Lauren"]},
                ],
                "residual": ["piqué", "for work"],
            },
            "note": "'all-white' requires equals_set ['White']; knit texture 'piqué' stays in residual.",
        },
    ],
    "Tank tops & Camisoles": [
        {
            "query": "green tank top, but not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Excluding a shade ('not emerald') does not exclude the Green family; generic tank top does not set strap_style.",
        },
        {
            "query": "women's fitted silk camisole with spaghetti straps and V-neck under $90",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Slim"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Silk"]},
                    {"feature": "strap_width", "operator": "in", "values": ["Spaghetti"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "price", "operator": "lte", "value": 90},
                ],
                "residual": [],
            },
            "note": "'spaghetti straps' sets strap_width=Spaghetti without implying strap_style=Standard.",
        },
        {
            "query": "all-black racerback cropped tank in cotton and elastane for yoga",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "strap_style", "operator": "in", "values": ["Racerback"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                ],
                "residual": ["for yoga"],
            },
            "note": "'all-black' -> equals_set; 'cotton and elastane' -> contains_all.",
        },
        {
            "query": "strapless burgundy tube top without polyester, around 70 PLN",
            "output": {
                "filters": [
                    {"feature": "strap_style", "operator": "in", "values": ["Strapless"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "around", "value": 70},
                ],
                "residual": ["burgundy"],
            },
            "note": "Do not infer strap_width from Strapless; 'burgundy' maps to Red and stays in residual.",
        },
        {
            "query": "pink and white floral halter cami by Zara between 40 and 90 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Pink", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Floral"]},
                    {"feature": "strap_style", "operator": "in", "values": ["Halter"]},
                    {"feature": "brand", "operator": "in", "values": ["Zara"]},
                    {"feature": "price", "operator": "gte", "value": 40},
                    {"feature": "price", "operator": "lte", "value": 90},
                ],
                "residual": [],
            },
            "note": "'pink and white' uses contains_all.",
        },
    ],
    "Bodysuits": [
        {
            "query": "women's all-black long-sleeve turtleneck bodysuit in cotton and elastane",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Long Sleeve"]},
                    {"feature": "neckline", "operator": "in", "values": ["High Neck"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                ],
                "residual": ["turtleneck"],
            },
            "note": "'turtleneck' maps to High Neck and stays in residual; do not infer strap_style=Standard Sleeved unless explicitly stated.",
        },
        {
            "query": "sleeveless burgundy lace bodysuit with spaghetti straps and V-neck under $60",
            "output": {
                "filters": [
                    {"feature": "sleeve_length", "operator": "in", "values": ["Sleeveless"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "strap_width", "operator": "in", "values": ["Spaghetti"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "price", "operator": "lte", "value": 60},
                ],
                "residual": ["burgundy", "lace"],
            },
            "note": "'burgundy' and unsupported fabric 'lace' stay in residual.",
        },
        {
            "query": "one-shoulder animal print bodysuit with leopard print, without nylon, around 120 PLN",
            "output": {
                "filters": [
                    {"feature": "strap_style", "operator": "in", "values": ["One-Shoulder"]},
                    {"feature": "pattern", "operator": "in", "values": ["Animal Print"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Nylon"]},
                    {"feature": "price", "operator": "around", "value": 120},
                ],
                "residual": ["leopard print"],
            },
            "note": "'leopard print' maps to Animal Print and stays in residual.",
        },
        {
            "query": "white or beige strapless bodysuit by Skims, not turquoise",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Beige", "White"]},
                    {"feature": "strap_style", "operator": "in", "values": ["Strapless"]},
                    {"feature": "brand", "operator": "in", "values": ["Skims"]},
                ],
                "residual": ["not turquoise"],
            },
            "note": "Color alternatives use contains_any; excluded shade stays in residual.",
        },
        {
            "query": "100% cotton scoop-neck bodysuit with wide straps between 80 and 150 PLN",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "neckline", "operator": "in", "values": ["Scoop Neck"]},
                    {"feature": "strap_width", "operator": "in", "values": ["Wide"]},
                    {"feature": "price", "operator": "gte", "value": 80},
                    {"feature": "price", "operator": "lte", "value": 150},
                ],
                "residual": [],
            },
            "note": "'100% cotton' maps to equals_set ['Cotton'].",
        },
    ],
    "Shirts": [
        {
            "query": "men's slim fit dress shirt by Calvin Klein with point collar under $85",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "fit", "operator": "in", "values": ["Slim"]},
                    {"feature": "brand", "operator": "in", "values": ["Calvin Klein"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Point Collar"]},
                    {"feature": "price", "operator": "lte", "value": 85},
                ],
                "residual": ["dress"],
            },
            "note": "In Shirts, 'dress shirt' keeps 'dress' in residual.",
        },
        {
            "query": "100% linen short-sleeve camp collar shirt in olive for beach",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Linen"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Short Sleeve"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Camp Collar"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                ],
                "residual": ["olive", "for beach"],
            },
            "note": "'100% linen' -> equals_set; 'olive' -> Green + residual.",
        },
        {
            "query": "red and black plaid long-sleeve flannel shirt, not oversized, around 160 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "Red"]},
                    {"feature": "pattern", "operator": "in", "values": ["Plaid"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Long Sleeve"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                    {"feature": "price", "operator": "around", "value": 160},
                ],
                "residual": ["flannel"],
            },
            "note": "'red and black' uses contains_all; 'flannel' stays in residual.",
        },
        {
            "query": "women's oversized button-down oxford shirt in cotton without polyester",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Cotton"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                ],
                "residual": ["button-down", "oxford"],
            },
            "note": "'button-down' and 'oxford' stay in residual.",
        },
        {
            "query": "all-white collarless cropped shirt between 90 and 180 PLN, not turquoise",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["White"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Collarless"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "price", "operator": "gte", "value": 90},
                    {"feature": "price", "operator": "lte", "value": 180},
                ],
                "residual": ["not turquoise"],
            },
            "note": "'all-white' -> equals_set ['White'].",
        },
    ],
    "Blouses": [
        {
            "query": "women's 100% silk burgundy V-neck blouse with long sleeves under 300 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Silk"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Long Sleeve"]},
                    {"feature": "price", "operator": "lte", "value": 300},
                ],
                "residual": ["burgundy"],
            },
            "note": "'100% silk' -> equals_set; 'burgundy' -> Red + residual.",
        },
        {
            "query": "black and white polka dot collared blouse, cotton and viscose without polyester",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Polka Dot"]},
                    {"feature": "neckline", "operator": "in", "values": ["Collared"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Viscose"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                ],
                "residual": [],
            },
            "note": "'black and white' and 'cotton and viscose' both use contains_all.",
        },
        {
            "query": "sleeveless cropped leopard print blouse by Mango around $45, not oversized",
            "output": {
                "filters": [
                    {"feature": "sleeve_length", "operator": "in", "values": ["Sleeveless"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "pattern", "operator": "in", "values": ["Animal Print"]},
                    {"feature": "brand", "operator": "in", "values": ["Mango"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                    {"feature": "price", "operator": "around", "value": 45},
                ],
                "residual": ["leopard print"],
            },
            "note": "'leopard print' maps to Animal Print and stays in residual.",
        },
        {
            "query": "fitted turtleneck blouse with three-quarter sleeves in cream for office",
            "output": {
                "filters": [
                    {"feature": "fit", "operator": "in", "values": ["Slim"]},
                    {"feature": "neckline", "operator": "in", "values": ["High Neck"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Three-Quarter Sleeve"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["White"]},
                ],
                "residual": ["turtleneck", "cream", "for office"],
            },
            "note": "'turtleneck' -> High Neck + residual; 'cream' -> White + residual.",
        },
        {
            "query": "green floral peasant blouse between 70 and 140 PLN, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "pattern", "operator": "in", "values": ["Floral"]},
                    {"feature": "price", "operator": "gte", "value": 70},
                    {"feature": "price", "operator": "lte", "value": 140},
                ],
                "residual": ["peasant", "not emerald"],
            },
            "note": "Excluded shade 'not emerald' stays only in residual.",
        },
    ],
    "Knit Sweaters": [
        {
            "query": "100% wool burgundy turtleneck sweater for women under 350 PLN",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Wool"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "neckline", "operator": "in", "values": ["High Neck"]},
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "price", "operator": "lte", "value": 350},
                ],
                "residual": ["burgundy", "turtleneck"],
            },
            "note": "'100% wool' -> equals_set; 'burgundy' and 'turtleneck' map to Red/High Neck and stay in residual.",
        },
        {
            "query": "men's oversized cable-knit crewneck jumper in wool and cashmere without acrylic",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "neckline", "operator": "in", "values": ["Crewneck"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cashmere", "Wool"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Acrylic"]},
                ],
                "residual": ["cable-knit"],
            },
            "note": "'wool and cashmere' uses contains_all; 'without acrylic' uses contains_none; 'cable-knit' stays in residual.",
        },
        {
            "query": "cropped striped V-neck knit sweater without a hood, around $75",
            "output": {
                "filters": [
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "around", "value": 75},
                ],
                "residual": [],
            },
            "note": "'without a hood' sets hood=Without Hood.",
        },
        {
            "query": "all-black hooded knit sweater by Massimo Dutti between 150 and 300 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "brand", "operator": "in", "values": ["Massimo Dutti"]},
                    {"feature": "price", "operator": "gte", "value": 150},
                    {"feature": "price", "operator": "lte", "value": 300},
                ],
                "residual": [],
            },
            "note": "'all-black' -> equals_set ['Black']; 'hooded' -> hood=With Hood.",
        },
        {
            "query": "30% wool green sweater with short sleeves, not emerald, not slim",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Wool"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Short Sleeve"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Slim"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "30% share uses contains_any; excluded shade stays in residual.",
        },
    ],
    "Sweatshirts": [
        {
            "query": "men's heather grey Nike crewneck sweatshirt in cotton and polyester under 220 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Grey"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                    {"feature": "neckline", "operator": "in", "values": ["Crewneck"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Polyester"]},
                    {"feature": "price", "operator": "lte", "value": 220},
                ],
                "residual": ["heather grey"],
            },
            "note": "'heather grey' maps to Grey and stays in residual.",
        },
        {
            "query": "women's oversized cropped fleece sweatshirt without a hood, around $55",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "around", "value": 55},
                ],
                "residual": ["fleece"],
            },
            "note": "'fleece' fabric texture stays in residual.",
        },
        {
            "query": "100% cotton all-black mock-neck sweatshirt, not slim",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "neckline", "operator": "in", "values": ["High Neck"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Slim"]},
                ],
                "residual": ["mock-neck"],
            },
            "note": "'mock-neck' maps to High Neck and stays in residual.",
        },
        {
            "query": "navy and white striped sweatshirt by Champion between 100 and 200 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Blue", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "brand", "operator": "in", "values": ["Champion"]},
                    {"feature": "price", "operator": "gte", "value": 100},
                    {"feature": "price", "operator": "lte", "value": 200},
                ],
                "residual": ["navy"],
            },
            "note": "'navy and white' maps to contains_all ['Blue', 'White'] and keeps 'navy' in residual.",
        },
        {
            "query": "green short-sleeve sweatshirt without polyester, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Short Sleeve"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Excluded shade 'not emerald' stays only in residual.",
        },
    ],
    "Hoodies & Zipups": [
        {
            "query": "all-black cotton and elastane zip-up hoodie up to 180 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                    {"feature": "closure_type", "operator": "in", "values": ["Zip"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "price", "operator": "lte", "value": 180},
                ],
                "residual": [],
            },
            "note": "In Hoodies & Zipups, 'hoodie' explicitly requests hood=With Hood (Without Hood stays not_specified, NOT excluded).",
        },
        {
            "query": "men's navy Nike half-zip sweatshirt without a hood, around $70",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "brand", "operator": "in", "values": ["Nike"]},
                    {"feature": "closure_type", "operator": "in", "values": ["Half-Zip"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "around", "value": 70},
                ],
                "residual": ["navy"],
            },
            "note": "'half-zip' -> Half-Zip; 'without a hood' -> Without Hood; 'navy' -> Blue + residual.",
        },
        {
            "query": "women's oversized cropped pullover hoodie in 100% cotton, not slim",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Slim"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "closure_type", "operator": "in", "values": ["Pullover"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                ],
                "residual": [],
            },
            "note": "'100% cotton' -> equals_set ['Cotton'].",
        },
        {
            "query": "grey and black camo zip-up sweatshirt without polyester between 120 and 240 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "Grey"]},
                    {"feature": "pattern", "operator": "in", "values": ["Camo"]},
                    {"feature": "closure_type", "operator": "in", "values": ["Zip"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "gte", "value": 120},
                    {"feature": "price", "operator": "lte", "value": 240},
                ],
                "residual": [],
            },
            "note": "A 'zip-up sweatshirt' without mentioning a hood leaves hood unspecified.",
        },
        {
            "query": "2x olive sleeveless gym hoodie for men, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Sleeveless"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                ],
                "residual": ["2x", "olive", "gym", "not emerald"],
            },
            "note": "'2x', 'olive', 'gym', and 'not emerald' stay in residual.",
        },
    ],
    "Cardigans": [
        {
            "query": "women's oversized open-front cardigan in wool and cashmere under 320 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "closure_type", "operator": "in", "values": ["Open Front"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cashmere", "Wool"]},
                    {"feature": "price", "operator": "lte", "value": 320},
                ],
                "residual": [],
            },
            "note": "'open-front' -> Open Front; 'wool and cashmere' -> contains_all.",
        },
        {
            "query": "cropped button-front V-neck cardigan in burgundy without acrylic, around $60",
            "output": {
                "filters": [
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "closure_type", "operator": "in", "values": ["Button"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Acrylic"]},
                    {"feature": "price", "operator": "around", "value": 60},
                ],
                "residual": ["burgundy"],
            },
            "note": "'button-front' -> Button; 'burgundy' -> Red + residual.",
        },
        {
            "query": "100% cotton all-white longline hooded cardigan with pockets",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["White"]},
                    {"feature": "length", "operator": "in", "values": ["Longline"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                ],
                "residual": ["with pockets"],
            },
            "note": "'100% cotton' and 'all-white' both use equals_set; 'with pockets' stays in residual.",
        },
        {
            "query": "men's navy and grey striped collared cardigan by Tommy Hilfiger between 200 and 400 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_all", "values": ["Blue", "Grey"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "neckline", "operator": "in", "values": ["Collared"]},
                    {"feature": "brand", "operator": "in", "values": ["Tommy Hilfiger"]},
                    {"feature": "price", "operator": "gte", "value": 200},
                    {"feature": "price", "operator": "lte", "value": 400},
                ],
                "residual": ["navy"],
            },
            "note": "'navy and grey' -> contains_all ['Blue', 'Grey'] + residual ['navy'].",
        },
        {
            "query": "green short-sleeve crewneck cardigan without a hood, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Short Sleeve"]},
                    {"feature": "neckline", "operator": "in", "values": ["Crewneck"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Excluded shade stays in residual.",
        },
    ],
    "Classic Coats": [
        {
            "query": "women's camel double-breasted wool pea coat with lapel collar and silk lining under 900 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Brown"]},
                    {"feature": "closure_type", "operator": "contains_any", "values": ["Double-Breasted"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Wool"]},
                    {"feature": "coat_style", "operator": "in", "values": ["Standard"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Lapel Collar"]},
                    {"feature": "lining_composition", "operator": "contains_any", "values": ["Silk"]},
                    {"feature": "price", "operator": "lte", "value": 900},
                ],
                "residual": ["camel", "pea coat"],
            },
            "note": "'pea coat' maps to coat_style=Standard AND stays in residual; 'camel' maps to Brown AND stays in residual.",
        },
        {
            "query": "men's olive hooded down parka with zip and press-stud closure, between 400 and 800 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "insulation", "operator": "in", "values": ["Down"]},
                    {"feature": "coat_style", "operator": "in", "values": ["Parka"]},
                    {"feature": "closure_type", "operator": "contains_all", "values": ["Press-Stud", "Zip"]},
                    {"feature": "price", "operator": "gte", "value": 400},
                    {"feature": "price", "operator": "lte", "value": 800},
                ],
                "residual": ["olive"],
            },
            "note": "In outerwear, 'down' maps to insulation=Down (not main_composition); combined closures use contains_all.",
        },
        {
            "query": "unlined all-black oversized long coat in 100% wool without a hood, around $250",
            "output": {
                "filters": [
                    {"feature": "lining_composition", "operator": "equals_set", "values": ["Unlined"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "length", "operator": "in", "values": ["Long"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Wool"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "around", "value": 250},
                ],
                "residual": [],
            },
            "note": "'unlined' -> lining_composition equals_set ['Unlined']; bare 'coat' does NOT set coat_style=Standard.",
        },
        {
            "query": "black and white plaid mid-length coat by Max Mara with belt, not oversized",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Plaid"]},
                    {"feature": "length", "operator": "in", "values": ["Mid-Length"]},
                    {"feature": "brand", "operator": "in", "values": ["Max Mara"]},
                    {"feature": "closure_type", "operator": "contains_any", "values": ["Belted"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                ],
                "residual": [],
            },
            "note": "'black and white' -> contains_all; 'with belt' -> closure_type contains_any ['Belted'].",
        },
        {
            "query": "green shearling-lined short coat with stand collar, without polyester, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "insulation", "operator": "in", "values": ["Shearling Lined"]},
                    {"feature": "length", "operator": "in", "values": ["Short"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Stand Collar"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "'shearling-lined' maps to insulation=Shearling Lined (not lining_composition).",
        },
    ],
    "Trench Coats": [
        {
            "query": "women's beige double-breasted belted trench coat in 100% cotton with lapel collar under 700 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Beige"]},
                    {"feature": "closure_type", "operator": "contains_all", "values": ["Belted", "Double-Breasted"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Lapel Collar"]},
                    {"feature": "price", "operator": "lte", "value": 700},
                ],
                "residual": [],
            },
            "note": "'double-breasted belted' requires both closures -> contains_all ['Belted', 'Double-Breasted'].",
        },
        {
            "query": "unlined navy mid-length trench coat by Burberry without a hood, around $600",
            "output": {
                "filters": [
                    {"feature": "lining_composition", "operator": "equals_set", "values": ["Unlined"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "length", "operator": "in", "values": ["Mid-Length"]},
                    {"feature": "brand", "operator": "in", "values": ["Burberry"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "around", "value": 600},
                ],
                "residual": ["navy"],
            },
            "note": "'unlined' -> lining_composition equals_set ['Unlined']; 'navy' -> Blue + residual.",
        },
        {
            "query": "men's oversized long leather trench coat in all-black with viscose lining",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "length", "operator": "in", "values": ["Long"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Leather"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "lining_composition", "operator": "contains_any", "values": ["Viscose"]},
                ],
                "residual": [],
            },
            "note": "'all-black' -> equals_set ['Black']; 'with viscose lining' -> lining_composition contains_any ['Viscose'].",
        },
        {
            "query": "olive and black plaid hooded short trench with point collar between 250 and 500 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "Green"]},
                    {"feature": "pattern", "operator": "in", "values": ["Plaid"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "length", "operator": "in", "values": ["Short"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Point Collar"]},
                    {"feature": "price", "operator": "gte", "value": 250},
                    {"feature": "price", "operator": "lte", "value": 500},
                ],
                "residual": ["olive"],
            },
            "note": "'olive and black' -> contains_all ['Black', 'Green'] + residual ['olive'].",
        },
        {
            "query": "uninsulated green trench coat without polyester, not emerald, not oversized",
            "output": {
                "filters": [
                    {"feature": "insulation", "operator": "in", "values": ["Uninsulated"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Excluded shade stays only in residual.",
        },
    ],
    "Jackets": [
        {
            "query": "men's all-black leather biker jacket with zipper and lapel collar under 600 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Leather"]},
                    {"feature": "jacket_style", "operator": "in", "values": ["Biker"]},
                    {"feature": "closure_type", "operator": "contains_any", "values": ["Zip"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Lapel Collar"]},
                    {"feature": "price", "operator": "lte", "value": 600},
                ],
                "residual": [],
            },
            "note": "'all-black' -> equals_set ['Black']; 'biker' -> jacket_style=Biker.",
        },
        {
            "query": "women's oversized cropped denim jacket in 100% cotton with shearling-lined interior, around $110",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "jacket_style", "operator": "in", "values": ["Denim"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "insulation", "operator": "in", "values": ["Shearling Lined"]},
                    {"feature": "price", "operator": "around", "value": 110},
                ],
                "residual": [],
            },
            "note": "'shearling-lined' maps to insulation=Shearling Lined (not lining_composition).",
        },
        {
            "query": "unlined navy and white nylon windbreaker jacket with hood by Columbia between 150 and 300 PLN",
            "output": {
                "filters": [
                    {"feature": "lining_composition", "operator": "equals_set", "values": ["Unlined"]},
                    {"feature": "colors", "operator": "contains_all", "values": ["Blue", "White"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Nylon"]},
                    {"feature": "jacket_style", "operator": "in", "values": ["Windbreaker"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "brand", "operator": "in", "values": ["Columbia"]},
                    {"feature": "price", "operator": "gte", "value": 150},
                    {"feature": "price", "operator": "lte", "value": 300},
                ],
                "residual": ["navy"],
            },
            "note": "'unlined' -> lining_composition equals_set ['Unlined']; 'navy and white' -> contains_all ['Blue', 'White'] + residual ['navy'].",
        },
        {
            "query": "burgundy faux leather jacket with silk lining and stand collar, without polyester",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "lining_composition", "operator": "contains_any", "values": ["Silk"]},
                    {"feature": "collar_type", "operator": "in", "values": ["Stand Collar"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                ],
                "residual": ["burgundy", "faux leather"],
            },
            "note": "'faux leather' does NOT map to Leather and stays in residual.",
        },
        {
            "query": "green goose down quilted jacket without a hood, not emerald, not oversized",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "insulation", "operator": "in", "values": ["Down"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                ],
                "residual": ["goose down", "quilted", "not emerald"],
            },
            "note": "'goose down' maps to insulation=Down and keeps 'goose down' in residual; 'quilted' and 'not emerald' stay in residual.",
        },
    ],
    "Bombers": [
        {
            "query": "unlined olive bomber jacket with leopard print for spring",
            "output": {
                "filters": [
                    {"feature": "lining_composition", "operator": "equals_set", "values": ["Unlined"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "pattern", "operator": "in", "values": ["Animal Print"]},
                ],
                "residual": ["olive", "leopard print", "for spring"],
            },
            "note": "'unlined' -> lining_composition equals_set ['Unlined']; 'olive' and 'leopard print' stay in residual.",
        },
        {
            "query": "men's all-black leather bomber by Alpha Industries with down insulation under 800 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Leather"]},
                    {"feature": "brand", "operator": "in", "values": ["Alpha Industries"]},
                    {"feature": "insulation", "operator": "in", "values": ["Down"]},
                    {"feature": "price", "operator": "lte", "value": 800},
                ],
                "residual": [],
            },
            "note": "'all-black' -> equals_set ['Black']; 'down insulation' -> insulation=Down.",
        },
        {
            "query": "women's oversized cropped nylon bomber with zip and press-stud closure, around $95",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Nylon"]},
                    {"feature": "closure_type", "operator": "contains_all", "values": ["Press-Stud", "Zip"]},
                    {"feature": "price", "operator": "around", "value": 95},
                ],
                "residual": [],
            },
            "note": "Combined closures in Bombers use contains_all.",
        },
        {
            "query": "navy and white varsity bomber jacket with wool and polyester, without a hood, between 200 and 450 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Blue", "White"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Polyester", "Wool"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "gte", "value": 200},
                    {"feature": "price", "operator": "lte", "value": 450},
                ],
                "residual": ["navy", "varsity"],
            },
            "note": "'navy' and 'varsity' stay in residual.",
        },
        {
            "query": "green hooded bomber with silk lining, without acrylic, not emerald, not oversized",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "lining_composition", "operator": "contains_any", "values": ["Silk"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Acrylic"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "'with silk lining' -> lining_composition contains_any ['Silk'].",
        },
    ],
    "Vests": [
        {
            "query": "men's navy Patagonia goose down vest with zipper and without a hood under 500 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "brand", "operator": "in", "values": ["Patagonia"]},
                    {"feature": "insulation", "operator": "in", "values": ["Down"]},
                    {"feature": "closure_type", "operator": "contains_any", "values": ["Zip"]},
                    {"feature": "hood", "operator": "in", "values": ["Without Hood"]},
                    {"feature": "price", "operator": "lte", "value": 500},
                ],
                "residual": ["navy", "goose down"],
            },
            "note": "'goose down' maps to insulation=Down and stays in residual.",
        },
        {
            "query": "unlined all-black tailored waistcoat in 100% wool with button closure, around $120",
            "output": {
                "filters": [
                    {"feature": "lining_composition", "operator": "equals_set", "values": ["Unlined"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Wool"]},
                    {"feature": "closure_type", "operator": "contains_any", "values": ["Button"]},
                    {"feature": "price", "operator": "around", "value": 120},
                ],
                "residual": ["tailored"],
            },
            "note": "'unlined', 'all-black', and '100% wool' all use equals_set.",
        },
        {
            "query": "women's oversized longline hooded vest with synthetic padding between 150 and 300 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "fit", "operator": "in", "values": ["Oversized"]},
                    {"feature": "length", "operator": "in", "values": ["Longline"]},
                    {"feature": "hood", "operator": "in", "values": ["With Hood"]},
                    {"feature": "insulation", "operator": "in", "values": ["Synthetic Padding"]},
                    {"feature": "price", "operator": "gte", "value": 150},
                    {"feature": "price", "operator": "lte", "value": 300},
                ],
                "residual": [],
            },
            "note": "'synthetic padding' maps to insulation=Synthetic Padding.",
        },
        {
            "query": "olive and black camo gilet in nylon and cotton without polyester, with silk lining",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "Green"]},
                    {"feature": "pattern", "operator": "in", "values": ["Camo"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Nylon"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "lining_composition", "operator": "contains_any", "values": ["Silk"]},
                ],
                "residual": ["olive"],
            },
            "note": "'olive and black' -> contains_all ['Black', 'Green'] + residual ['olive'].",
        },
        {
            "query": "cropped green fleece-lined vest, not emerald, not oversized",
            "output": {
                "filters": [
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "insulation", "operator": "in", "values": ["Fleece Lined"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Oversized"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "'fleece-lined' maps to insulation=Fleece Lined; 'not emerald' stays in residual.",
        },
    ],
    "Trousers": [
        {
            "query": "women's high-rise wide-leg tailored trousers in 100% wool by Massimo Dutti under 450 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "rise", "operator": "in", "values": ["High-Rise"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Wide-Leg"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Wool"]},
                    {"feature": "brand", "operator": "in", "values": ["Massimo Dutti"]},
                    {"feature": "price", "operator": "lte", "value": 450},
                ],
                "residual": ["tailored"],
            },
            "note": "'100% wool' -> equals_set ['Wool']; 'tailored' stays in residual.",
        },
        {
            "query": "men's slim fit navy chinos in cotton and elastane without polyester, around $80",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "fit", "operator": "in", "values": ["Slim"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "around", "value": 80},
                ],
                "residual": ["navy", "chinos"],
            },
            "note": "Slim fit maps ONLY to fit=Slim (do NOT infer leg_shape=Tapered).",
        },
        {
            "query": "all-black bootcut cropped pants with elasticized waistband between 120 and 250 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Flared"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "waistband_type", "operator": "in", "values": ["Elasticized"]},
                    {"feature": "price", "operator": "gte", "value": 120},
                    {"feature": "price", "operator": "lte", "value": 250},
                ],
                "residual": ["bootcut"],
            },
            "note": "'bootcut' maps to leg_shape=Flared AND stays in residual; elasticized waistband does not imply Tapered.",
        },
        {
            "query": "grey and white plaid straight-leg full-length trousers with structured waistband, not skinny",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Grey", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Plaid"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Straight"]},
                    {"feature": "length", "operator": "in", "values": ["Full-Length"]},
                    {"feature": "waistband_type", "operator": "in", "values": ["Structured"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Skinny"]},
                ],
                "residual": [],
            },
            "note": "'grey and white' -> contains_all.",
        },
        {
            "query": "green tapered trousers with zippered cuffs, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Tapered"]},
                    {"feature": "cuff_style", "operator": "in", "values": ["Zippered Cuff"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Explicit 'tapered' sets leg_shape=Tapered; 'not emerald' stays in residual.",
        },
    ],
    "Cargo Pants": [
        {
            "query": "men's olive relaxed fit cargo pants in 100% cotton with elasticized cuffs under 200 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "fit", "operator": "in", "values": ["Relaxed"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "cuff_style", "operator": "in", "values": ["Elasticized Cuff"]},
                    {"feature": "price", "operator": "lte", "value": 200},
                ],
                "residual": ["olive"],
            },
            "note": "'olive' -> Green + residual; '100% cotton' -> equals_set.",
        },
        {
            "query": "black cargo trousers with elasticized waistband up to 220 PLN, not skinny",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Black"]},
                    {"feature": "waistband_type", "operator": "in", "values": ["Elasticized"]},
                    {"feature": "price", "operator": "lte", "value": 220},
                    {"feature": "fit", "operator": "not_in", "values": ["Skinny"]},
                ],
                "residual": [],
            },
            "note": "'elasticized waistband' ('z gumką w pasie') sets ONLY waistband_type=Elasticized, NOT leg_shape=Tapered.",
        },
        {
            "query": "women's high-rise wide-leg camo cargo pants in cotton and nylon without polyester, around $75",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "rise", "operator": "in", "values": ["High-Rise"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Wide-Leg"]},
                    {"feature": "pattern", "operator": "in", "values": ["Camo"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Nylon"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "around", "value": 75},
                ],
                "residual": [],
            },
            "note": "'cotton and nylon' -> contains_all; 'without polyester' -> contains_none.",
        },
        {
            "query": "all-black tapered cropped cargo pants by Carhartt between 180 and 350 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Tapered"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "brand", "operator": "in", "values": ["Carhartt"]},
                    {"feature": "price", "operator": "gte", "value": 180},
                    {"feature": "price", "operator": "lte", "value": 350},
                ],
                "residual": [],
            },
            "note": "'all-black' -> equals_set ['Black'].",
        },
        {
            "query": "green and beige straight-leg cargo pants with open hem, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Beige", "Green"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Straight"]},
                    {"feature": "cuff_style", "operator": "in", "values": ["Open Hem"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "'green and beige' -> contains_all; 'not emerald' stays in residual.",
        },
    ],
    "Sweatpants & Lounge Pants": [
        {
            "query": "2x grey Adidas joggers for men with zippered cuffs under 180 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Grey"]},
                    {"feature": "brand", "operator": "in", "values": ["Adidas"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Tapered"]},
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "cuff_style", "operator": "in", "values": ["Zippered Cuff"]},
                    {"feature": "price", "operator": "lte", "value": 180},
                ],
                "residual": ["2x", "joggers"],
            },
            "note": "In Sweatpants & Lounge Pants, 'joggers' maps to leg_shape=Tapered AND stays in residual; '2x' is not a price.",
        },
        {
            "query": "women's high-rise wide-leg fleece sweatpants in cotton without polyester, around $50",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "rise", "operator": "in", "values": ["High-Rise"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Wide-Leg"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Cotton"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "around", "value": 50},
                ],
                "residual": ["fleece"],
            },
            "note": "'fleece' stays in residual.",
        },
        {
            "query": "100% cotton all-black relaxed fit lounge pants with open hem, not skinny",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "fit", "operator": "in", "values": ["Relaxed"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Skinny"]},
                    {"feature": "cuff_style", "operator": "in", "values": ["Open Hem"]},
                ],
                "residual": [],
            },
            "note": "'100% cotton' and 'all-black' use equals_set.",
        },
        {
            "query": "navy and white striped track pants in cotton and elastane between 90 and 190 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Blue", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                    {"feature": "price", "operator": "gte", "value": 90},
                    {"feature": "price", "operator": "lte", "value": 190},
                ],
                "residual": ["navy", "track pants"],
            },
            "note": "'navy and white' and 'cotton and elastane' both use contains_all.",
        },
        {
            "query": "cropped green sweatpants with elasticized cuffs, not emerald",
            "output": {
                "filters": [
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "cuff_style", "operator": "in", "values": ["Elasticized Cuff"]},
                ],
                "residual": ["not emerald"],
            },
            "note": "Excluded shade stays only in residual.",
        },
    ],
    "Jeans": [
        {
            "query": "women's high-rise bootcut Levi's jeans, not ripped, 34 x 28, under 300 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "rise", "operator": "in", "values": ["High-Rise"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Flared"]},
                    {"feature": "brand", "operator": "in", "values": ["Levi's"]},
                    {"feature": "distressing", "operator": "contains_none", "values": ["Distressed"]},
                    {"feature": "price", "operator": "lte", "value": 300},
                ],
                "residual": ["bootcut", "34 x 28"],
            },
            "note": "'bootcut' -> leg_shape=Flared + residual; 'not ripped' -> distressing contains_none ['Distressed']; '34 x 28' is size in residual.",
        },
        {
            "query": "men's skinny fit biker jeans in black cotton and elastane, around $90",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "fit", "operator": "in", "values": ["Skinny"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Black"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Elastane"]},
                    {"feature": "price", "operator": "around", "value": 90},
                ],
                "residual": ["biker"],
            },
            "note": "'skinny fit' maps ONLY to fit=Skinny (do NOT infer leg_shape=Tapered); 'biker' stays in residual.",
        },
        {
            "query": "100% cotton all-white wide-leg cropped jeans with clean wash, without elastane",
            "output": {
                "filters": [
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Elastane"]},
                    {"feature": "colors", "operator": "equals_set", "values": ["White"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Wide-Leg"]},
                    {"feature": "length", "operator": "in", "values": ["Cropped"]},
                    {"feature": "distressing", "operator": "contains_any", "values": ["Clean"]},
                ],
                "residual": [],
            },
            "note": "'100% cotton' and 'all-white' use equals_set; 'clean wash' -> distressing contains_any ['Clean'].",
        },
        {
            "query": "faded and distressed low-rise relaxed straight jeans by Wrangler between 150 and 280 PLN",
            "output": {
                "filters": [
                    {"feature": "distressing", "operator": "contains_all", "values": ["Distressed", "Faded"]},
                    {"feature": "rise", "operator": "in", "values": ["Low-Rise"]},
                    {"feature": "fit", "operator": "in", "values": ["Relaxed"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Straight"]},
                    {"feature": "brand", "operator": "in", "values": ["Wrangler"]},
                    {"feature": "price", "operator": "gte", "value": 150},
                    {"feature": "price", "operator": "lte", "value": 280},
                ],
                "residual": [],
            },
            "note": "'faded and distressed' requires both -> distressing contains_all ['Distressed', 'Faded'].",
        },
        {
            "query": "blue or grey tapered jeans with elasticized waistband, not turquoise",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue", "Grey"]},
                    {"feature": "leg_shape", "operator": "in", "values": ["Tapered"]},
                    {"feature": "waistband_type", "operator": "in", "values": ["Elasticized"]},
                ],
                "residual": ["not turquoise"],
            },
            "note": "Excluded shade 'not turquoise' stays only in residual.",
        },
    ],
    "Shorts": [
        {
            "query": "men's navy Under Armour running shorts with elasticized waistband under 140 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Men"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                    {"feature": "brand", "operator": "in", "values": ["Under Armour"]},
                    {"feature": "shorts_type", "operator": "in", "values": ["Athletic"]},
                    {"feature": "waistband_type", "operator": "in", "values": ["Elasticized"]},
                    {"feature": "price", "operator": "lte", "value": 140},
                ],
                "residual": ["navy", "running"],
            },
            "note": "In Shorts, 'running' maps to shorts_type=Athletic AND stays in residual; 'navy' maps to Blue AND stays in residual.",
        },
        {
            "query": "women's high-rise denim shorts in 100% cotton without elastane, around $45",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "rise", "operator": "in", "values": ["High-Rise"]},
                    {"feature": "shorts_type", "operator": "in", "values": ["Denim"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Cotton"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Elastane"]},
                    {"feature": "price", "operator": "around", "value": 45},
                ],
                "residual": [],
            },
            "note": "'100% cotton' -> equals_set ['Cotton']; 'without elastane' -> contains_none ['Elastane'].",
        },
        {
            "query": "olive relaxed cargo shorts in cotton and nylon, mid-length, between 80 and 160 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "fit", "operator": "in", "values": ["Relaxed"]},
                    {"feature": "shorts_type", "operator": "in", "values": ["Cargo"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Nylon"]},
                    {"feature": "length", "operator": "in", "values": ["Mid-Length"]},
                    {"feature": "price", "operator": "gte", "value": 80},
                    {"feature": "price", "operator": "lte", "value": 160},
                ],
                "residual": ["olive"],
            },
            "note": "'cotton and nylon' -> contains_all; 'olive' -> Green + residual.",
        },
        {
            "query": "all-black tailored linen shorts with structured waistband, not skinny",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "shorts_type", "operator": "in", "values": ["Tailored"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Linen"]},
                    {"feature": "waistband_type", "operator": "in", "values": ["Structured"]},
                    {"feature": "fit", "operator": "not_in", "values": ["Skinny"]},
                ],
                "residual": [],
            },
            "note": "'all-black' -> equals_set ['Black'].",
        },
        {
            "query": "black and white striped sweatshorts for volleyball, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Striped"]},
                    {"feature": "shorts_type", "operator": "in", "values": ["Sweatshorts"]},
                ],
                "residual": ["for volleyball", "not emerald"],
            },
            "note": "'black and white' -> contains_all; 'not emerald' stays in residual.",
        },
    ],
    "Skirts": [
        {
            "query": "women's high-rise pleated midi skirt in 100% silk, burgundy, under 350 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "rise", "operator": "in", "values": ["High-Rise"]},
                    {"feature": "skirt_type", "operator": "contains_any", "values": ["Pleated"]},
                    {"feature": "length", "operator": "in", "values": ["Midi"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Silk"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "price", "operator": "lte", "value": 350},
                ],
                "residual": ["burgundy"],
            },
            "note": "skirt_type is multi-choice; '100% silk' -> equals_set; 'burgundy' -> Red + residual.",
        },
        {
            "query": "black and white plaid A-line mini wrap skirt in wool and polyester, around $65",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Plaid"]},
                    {"feature": "skirt_silhouette", "operator": "in", "values": ["A-Line"]},
                    {"feature": "length", "operator": "in", "values": ["Mini"]},
                    {"feature": "skirt_type", "operator": "contains_any", "values": ["Wrap"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Polyester", "Wool"]},
                    {"feature": "price", "operator": "around", "value": 65},
                ],
                "residual": [],
            },
            "note": "'black and white' and 'wool and polyester' both use contains_all.",
        },
        {
            "query": "tiered and ruffled floral maxi skirt without acrylic between 120 and 240 PLN",
            "output": {
                "filters": [
                    {"feature": "skirt_type", "operator": "contains_all", "values": ["Ruffled", "Tiered"]},
                    {"feature": "pattern", "operator": "in", "values": ["Floral"]},
                    {"feature": "length", "operator": "in", "values": ["Maxi"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Acrylic"]},
                    {"feature": "price", "operator": "gte", "value": 120},
                    {"feature": "price", "operator": "lte", "value": 240},
                ],
                "residual": [],
            },
            "note": "'tiered and ruffled' requires both on multi-choice skirt_type -> contains_all; do not infer gender=Women.",
        },
        {
            "query": "all-black fitted leather pencil skirt by Zara, not low-rise",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "skirt_silhouette", "operator": "in", "values": ["Fitted"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Leather"]},
                    {"feature": "brand", "operator": "in", "values": ["Zara"]},
                    {"feature": "rise", "operator": "not_in", "values": ["Low-Rise"]},
                ],
                "residual": ["pencil"],
            },
            "note": "'all-black' -> equals_set ['Black']; 'pencil' maps to Fitted and stays in residual.",
        },
        {
            "query": "green leopard print asymmetric skirt, not emerald",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "pattern", "operator": "in", "values": ["Animal Print"]},
                    {"feature": "skirt_type", "operator": "contains_any", "values": ["Asymmetric"]},
                ],
                "residual": ["leopard print", "not emerald"],
            },
            "note": "'leopard print' maps to Animal Print and stays in residual; 'not emerald' stays in residual.",
        },
    ],
    "Dresses": [
        {
            "query": "women's burgundy 100% silk slip midi dress with spaghetti straps and V-neck under 500 PLN",
            "output": {
                "filters": [
                    {"feature": "gender", "operator": "in", "values": ["Women"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Red"]},
                    {"feature": "main_composition", "operator": "equals_set", "values": ["Silk"]},
                    {"feature": "dress_type", "operator": "contains_any", "values": ["Slip"]},
                    {"feature": "length", "operator": "in", "values": ["Midi"]},
                    {"feature": "strap_width", "operator": "in", "values": ["Spaghetti"]},
                    {"feature": "neckline", "operator": "in", "values": ["V-Neck"]},
                    {"feature": "price", "operator": "lte", "value": 500},
                ],
                "residual": ["burgundy"],
            },
            "note": "'100% silk' -> equals_set; 'spaghetti straps' sets strap_width=Spaghetti without implying strap_style=Standard.",
        },
        {
            "query": "black and white floral A-line maxi wrap dress in cotton and viscose without polyester, around $110",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "contains_all", "values": ["Black", "White"]},
                    {"feature": "pattern", "operator": "in", "values": ["Floral"]},
                    {"feature": "dress_silhouette", "operator": "in", "values": ["A-Line"]},
                    {"feature": "length", "operator": "in", "values": ["Maxi"]},
                    {"feature": "dress_type", "operator": "contains_any", "values": ["Wrap"]},
                    {"feature": "main_composition", "operator": "contains_all", "values": ["Cotton", "Viscose"]},
                    {"feature": "main_composition", "operator": "contains_none", "values": ["Polyester"]},
                    {"feature": "price", "operator": "around", "value": 110},
                ],
                "residual": [],
            },
            "note": "Do NOT infer gender=Women from 'dress'.",
        },
        {
            "query": "all-black fitted long-sleeve turtleneck sweater dress by Mango between 150 and 300 PLN",
            "output": {
                "filters": [
                    {"feature": "colors", "operator": "equals_set", "values": ["Black"]},
                    {"feature": "dress_silhouette", "operator": "in", "values": ["Fitted"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Long Sleeve"]},
                    {"feature": "neckline", "operator": "in", "values": ["High Neck"]},
                    {"feature": "dress_type", "operator": "contains_any", "values": ["Sweater Dress"]},
                    {"feature": "brand", "operator": "in", "values": ["Mango"]},
                    {"feature": "price", "operator": "gte", "value": 150},
                    {"feature": "price", "operator": "lte", "value": 300},
                ],
                "residual": ["turtleneck"],
            },
            "note": "'all-black' -> equals_set ['Black']; 'turtleneck' -> High Neck + residual.",
        },
        {
            "query": "strapless mini cocktail dress in green, not emerald, not fitted",
            "output": {
                "filters": [
                    {"feature": "strap_style", "operator": "in", "values": ["Strapless"]},
                    {"feature": "length", "operator": "in", "values": ["Mini"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Green"]},
                    {"feature": "dress_silhouette", "operator": "not_in", "values": ["Fitted"]},
                ],
                "residual": ["cocktail", "not emerald"],
            },
            "note": "Do not infer Sleeveless or strap_width from Strapless; 'cocktail' and 'not emerald' stay in residual.",
        },
        {
            "query": "collared short-sleeve linen shirt dress in navy for summer",
            "output": {
                "filters": [
                    {"feature": "neckline", "operator": "in", "values": ["Collared"]},
                    {"feature": "sleeve_length", "operator": "in", "values": ["Short Sleeve"]},
                    {"feature": "main_composition", "operator": "contains_any", "values": ["Linen"]},
                    {"feature": "dress_type", "operator": "contains_any", "values": ["Shirt Dress"]},
                    {"feature": "colors", "operator": "contains_any", "values": ["Blue"]},
                ],
                "residual": ["navy", "for summer"],
            },
            "note": "'shirt dress' -> dress_type contains_any ['Shirt Dress']; 'navy' -> Blue + residual.",
        },
    ],
}


def build_jev_feature_examples_json(
    category: str,
    feature: str,
    catalog: Dict[str, Dict[str, Dict[str, Any]]],
) -> str:
    """Build category-scoped Jev feature examples strictly from PER_CATEGORY_FEW_SHOTS[category]."""
    cat_shots = PER_CATEGORY_FEW_SHOTS[category]
    is_multi = catalog[category][feature]["multi"]
    examples: List[Dict[str, Any]] = []

    for shot in cat_shots:
        pos_vals: List[str] = []
        neg_vals: List[str] = []
        relation: str | None = None
        for clause in shot["output"]["filters"]:
            if clause["feature"] != feature:
                continue
            op = clause["operator"]
            vals = clause.get("values", [])
            if op in ("in", "contains_any", "contains_all", "equals_set"):
                pos_vals.extend(vals)
                if is_multi:
                    relation = {
                        "contains_any": "ANY",
                        "contains_all": "ALL",
                        "equals_set": "EXACT",
                    }[op]
            elif op in ("not_in", "contains_none"):
                neg_vals.extend(vals)

        if not pos_vals and not neg_vals:
            continue

        value_labels: Dict[str, str] = {}
        for v in pos_vals:
            value_labels[v] = "requested"
        for v in neg_vals:
            value_labels[v] = "excluded"

        ex_obj: Dict[str, Any] = {
            "example_query": shot["query"],
            "value_labels": value_labels,
            "all_unlisted_value_labels": "not_specified",
        }
        if is_multi and relation is not None:
            ex_obj["relation"] = relation
        if shot.get("note"):
            ex_obj["explanation"] = shot["note"]
        examples.append(ex_obj)

    # Also include 1 negative-evidence example from the same category where this feature is not mentioned
    for shot in cat_shots:
        mentioned = any(c["feature"] == feature for c in shot["output"]["filters"])
        if not mentioned:
            examples.append(
                {
                    "example_query": shot["query"],
                    "value_labels": {},
                    "all_unlisted_value_labels": "not_specified",
                }
            )
            break

    return json.dumps(examples, ensure_ascii=False)
