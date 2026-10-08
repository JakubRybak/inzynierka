import csv
import json

CSV_FILE = "fashion_test_benchmark.csv"

# Wczytaj obecny plik
with open(CSV_FILE, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Dokładne mapowanie cech Ground Truth
ground_truth = {
    # 1. JACKETS & COATS
    "north face jacket womens": (
        {"department_gender": "Women"},
        "north face"
    ),
    "womens lightweight jacket without hood": (
        {"department_gender": "Women", "hood": "No", "insulation": "Lightweight / Transitional"},
        ""
    ),
    "rain jacket mens waterproof with hood": (
        {"department_gender": "Men", "hood": "Yes"},
        "rain waterproof"
    ),
    "ski coat women": (
        {"department_gender": "Women", "insulation": "Insulated / Winter"},
        "ski"
    ),
    "ladies pink motorcycle jacket": (
        {"department_gender": "Women", "primary_color": "Pink"},
        "motorcycle"
    ),
    "womens windbreaker jacket without hood": (
        {"department_gender": "Women", "hood": "No", "insulation": "Lightweight / Transitional"},
        "windbreaker"
    ),
    "fleece jacket women": (
        {"department_gender": "Women", "primary_material": "Fleece"},
        ""
    ),
    "sport coats for men big and tall": (
        {"department_gender": "Men"},
        "sport big and tall"
    ),
    "32 degrees jackets for women": (
        {"department_gender": "Women"},
        "32 degrees"
    ),

    # 2. HOODIES & SWEATSHIRTS
    "hoodies for women": (
        {"department_gender": "Women", "hood": "Yes"},
        ""
    ),
    "hoodies for men": (
        {"department_gender": "Men", "hood": "Yes"},
        ""
    ),
    "oversized sweatshirt for women": (
        {"department_gender": "Women", "hood": "No"},
        "oversized"
    ),
    "california sweatshirt for women": (
        {"department_gender": "Women", "hood": "No"},
        "california"
    ),
    "yellow champion hoodie": (
        {"primary_color": "Yellow", "hood": "Yes"},
        "champion"
    ),
    "track jacket men venum": (
        {"department_gender": "Men", "closure_type": "Zip-up"},
        "track venum"
    ),
    "womens red zip up hoodie": (
        {"department_gender": "Women", "primary_color": "Red", "hood": "Yes", "closure_type": "Zip-up"},
        ""
    ),
    "zipper sweaters for women without hoodie": (
        {"department_gender": "Women", "hood": "No", "closure_type": "Zip-up"},
        ""
    ),
    "g star hoodies for men": (
        {"department_gender": "Men", "hood": "Yes"},
        "g star"
    ),

    # 3. SWEATERS & CARDIGANS
    "womens sweaters": (
        {"department_gender": "Women"},
        ""
    ),
    "sweaters for women": (
        {"department_gender": "Women"},
        ""
    ),
    "cute fall sweaters": (
        {},
        "cute fall"
    ),
    "pink argyle sweater": (
        {"primary_color": "Pink", "pattern": "Plaid / Checked"},
        "argyle"
    ),
    "women elegant sweater": (
        {"department_gender": "Women"},
        "elegant"
    ),
    "3/4 sleeve cardigan for women": (
        {"department_gender": "Women", "closure_type": "Button-up (Cardigan)"},
        "3/4 sleeve"
    ),
    "crop cardigan": (
        {"closure_type": "Button-up (Cardigan)"},
        "crop"
    ),
    "white cardigan chunky": (
        {"primary_color": "White", "closure_type": "Button-up (Cardigan)", "knit_style": "Chunky / Cable Knit"},
        ""
    ),
    "port authority cardigan": (
        {"closure_type": "Button-up (Cardigan)"},
        "port authority"
    ),

    # 4. SHIRTS & BLOUSES
    "womens white button up blouse": (
        {"department_gender": "Women", "primary_color": "White", "closure_type": "Full Button Front"},
        ""
    ),
    "black mens dress shirt slim fit": (
        {"department_gender": "Men", "primary_color": "Black", "collar": "Classic Collar", "fit": "Slim Fit"},
        "dress"
    ),
    "lemon yellow blouse": (
        {"primary_color": "Yellow"},
        "lemon"
    ),
    "mens linen shirt": (
        {"department_gender": "Men", "primary_material": "Linen"},
        ""
    ),
    "white button down blouse women": (
        {"department_gender": "Women", "primary_color": "White", "collar": "Classic Collar", "closure_type": "Full Button Front"},
        ""
    ),
    "fleece lined flannel shirt women": (
        {"department_gender": "Women", "collar": "Classic Collar", "pattern": "Plaid / Checked"},
        "fleece lined flannel"
    ),
    "wide sleeve flannel shirt women": (
        {"department_gender": "Women", "collar": "Classic Collar", "pattern": "Plaid / Checked"},
        "wide sleeve flannel"
    ),
    "mens navy and gray oxford shirt": (
        {"department_gender": "Men", "primary_color": "Navy", "collar": "Classic Collar"},
        "gray oxford"
    ),
    "4xlt dress shirts for men big and tall": (
        {"department_gender": "Men", "collar": "Classic Collar"},
        "4xlt dress big and tall"
    ),

    # 5. T-SHIRTS & TOPS
    "jerzees long sleeve t shirt": (
        {"sleeve_length": "Long Sleeve", "closure_type": "Pull-over / No Buttons"},
        "jerzees"
    ),
    "v neck white t shirt women": (
        {"department_gender": "Women", "primary_color": "White", "neckline": "V-Neck", "closure_type": "Pull-over / No Buttons"},
        ""
    ),
    "brown tank top womens": (
        {"department_gender": "Women", "primary_color": "Brown", "sleeve_length": "Sleeveless / Tank Top", "closure_type": "Pull-over / No Buttons"},
        ""
    ),
    "cut out tank tops for women": (
        {"department_gender": "Women", "sleeve_length": "Sleeveless / Tank Top", "closure_type": "Pull-over / No Buttons"},
        "cut out"
    ),
    "tank top plus size women": (
        {"department_gender": "Women", "sleeve_length": "Sleeveless / Tank Top", "closure_type": "Pull-over / No Buttons"},
        "plus size"
    ),
    "golf polo slim fit": (
        {"closure_type": "Partial Button (Polo)"},
        "golf slim fit"
    ),
    "nautica polo shirts for men": (
        {"department_gender": "Men", "closure_type": "Partial Button (Polo)"},
        "nautica"
    ),
    "mens cotton polo shirts with pockets and short sleeves": (
        {"department_gender": "Men", "primary_material": "Cotton", "sleeve_length": "Short Sleeve", "closure_type": "Partial Button (Polo)"},
        "pockets"
    ),
    "dewalt shirt for men": (
        {"department_gender": "Men"},
        "dewalt"
    ),

    # 6. PANTS & TROUSERS
    "womens skinny jeans": (
        {"department_gender": "Women", "pant_type": "Jeans", "leg_fit": "Skinny", "primary_material": "Denim"},
        ""
    ),
    "trousers women": (
        {"department_gender": "Women", "pant_type": "Chinos / Trousers"},
        ""
    ),
    "plaid trousers for women": (
        {"department_gender": "Women", "pattern": "Plaid / Checked", "pant_type": "Chinos / Trousers"},
        ""
    ),
    "mens blue jeans regular fit": (
        {"department_gender": "Men", "primary_color": "Blue", "pant_type": "Jeans", "primary_material": "Denim", "leg_fit": "Straight"},
        "regular fit"
    ),
    "black cargo pants women": (
        {"department_gender": "Women", "primary_color": "Black", "pant_type": "Cargo"},
        ""
    ),
    "womens sweatpants without pockets": (
        {"department_gender": "Women", "pant_type": "Sweatpants / Joggers"},
        "without pockets"
    ),
    "mens shorts": (
        {"department_gender": "Men", "pant_type": "Shorts", "length": "Shorts"},
        ""
    ),
    "women fleece sweatpants": (
        {"department_gender": "Women", "pant_type": "Sweatpants / Joggers", "primary_material": "Fleece"},
        ""
    ),
    "carhartt double front pants for men": (
        {"department_gender": "Men", "pant_type": "Chinos / Trousers"},
        "carhartt double front"
    ),

    # 7. DRESSES
    "womens dresses": (
        {"department_gender": "Women"},
        ""
    ),
    "dresses for women casual summer": (
        {"department_gender": "Women"},
        "casual summer"
    ),
    "white dresses for women": (
        {"department_gender": "Women", "primary_color": "White"},
        ""
    ),
    "party dress for women sexy elegant": (
        {"department_gender": "Women"},
        "party sexy elegant"
    ),
    "black funeral dress": (
        {"primary_color": "Black"},
        "funeral"
    ),
    "women's striped short sleeve loose swing t-shirt dress": (
        {"department_gender": "Women", "pattern": "Striped", "sleeve_length": "Short Sleeve", "silhouette": "A-Line / Flared"},
        "loose t-shirt dress"
    ),
    "tank maxi dress summer": (
        {"length": "Maxi", "sleeve_length": "Sleeveless / Straps"},
        "summer"
    ),
    "cami tiered dress": (
        {"sleeve_length": "Sleeveless / Straps"},
        "tiered"
    ),
    "dresses for women party wedding": (
        {"department_gender": "Women"},
        "party wedding"
    ),

    # 8. FOOTWEAR
    "shoes for women": (
        {"department_gender": "Women"},
        "shoes"
    ),
    "shoes for men": (
        {"department_gender": "Men"},
        "shoes"
    ),
    "boots for women": (
        {"department_gender": "Women", "shaft_height": "Mid (ankle boot)"},
        ""
    ),
    "heel boots for women": (
        {"department_gender": "Women", "shaft_height": "Mid (ankle boot)", "heel_sole_type": "Heeled (Stiletto / Block)"},
        ""
    ),
    "black slip on sneakers for women": (
        {"department_gender": "Women", "primary_color": "Black", "shaft_height": "Low (sneakers / shoes)", "fastening": "Slip-on"},
        "sneakers"
    ),
    "water shoes": (
        {"shaft_height": "Low (sneakers / shoes)"},
        "water"
    ),
    "cap toe brown shoes": (
        {"primary_color": "Brown", "toe_style": "Closed Toe"},
        "cap toe"
    ),
    "cowboy boots women": (
        {"department_gender": "Women", "shaft_height": "High (knee-high / tall boot)"},
        "cowboy"
    ),
    "adidas shoes men": (
        {"department_gender": "Men"},
        "adidas"
    ),

    # 9. NONE / OUT OF SCOPE
    "ratchet belts for men without buckle": ({}, "ratchet belts for men without buckle"),
    "mens belt without buckle leather": ({}, "mens belt without buckle leather"),
    "leather belts for men": ({}, "leather belts for men"),
    "compression socks women": ({}, "compression socks women"),
    "wool socks": ({}, "wool socks"),
    "curious george yellow hat": ({}, "curious george yellow hat"),
    "plain black fitted hats for men": ({}, "plain black fitted hats for men"),
    "thick belts for women": ({}, "thick belts for women")
}

# Aktualizujemy wiersze
updated_rows = []
for r in rows:
    q = r["query"].strip()
    if q in ground_truth:
        attrs, res = ground_truth[q]
        r["expected_attributes"] = json.dumps(attrs)
        r["expected_residual"] = res
    else:
        print(f"UWAGA: brak mapowania dla '{q}'")
    updated_rows.append(r)

fieldnames = ["query_id", "query", "category", "difficulty", "borderline_note", "expected_attributes", "expected_residual"]
with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

print(f"Pomyślnie zaktualizowano wszystkie {len(updated_rows)} wierszy w {CSV_FILE}!")
