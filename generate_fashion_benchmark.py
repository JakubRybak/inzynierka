import csv
import json

# Definiujemy 80 starannie dobranych zapytań z Amazon ESCI
# Podział: 8 kategorii po 9 zapytań + 8 zapytań Out of Scope = 80 zapytań
BENCHMARK_DATA = [
    # =========================================================================
    # 1. JACKETS & COATS (9 zapytań)
    # =========================================================================
    {
        "query": "north face jacket womens",
        "category": "Jackets & Coats",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "north face"
    },
    {
        "query": "womens lightweight jacket without hood",
        "category": "Jackets & Coats",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "hood": "No", "insulation": "Lightweight / Transitional"},
        "expected_residual": ""
    },
    {
        "query": "rain jacket mens waterproof with hood",
        "category": "Jackets & Coats",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Men", "hood": "Yes"},
        "expected_residual": "rain waterproof"
    },
    {
        "query": "ski coat women",
        "category": "Jackets & Coats",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "insulation": "Insulated / Winter"},
        "expected_residual": "ski"
    },
    {
        "query": "ladies pink motorcycle jacket",
        "category": "Jackets & Coats",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "Pink"},
        "expected_residual": "motorcycle"
    },
    {
        "query": "womens windbreaker jacket without hood",
        "category": "Jackets & Coats",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Hoodies/Sports: windbreaker jacket",
        "expected_attributes": {"department_gender": "Women", "hood": "No", "insulation": "Lightweight / Transitional"},
        "expected_residual": "windbreaker"
    },
    {
        "query": "fleece jacket women",
        "category": "Jackets & Coats",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Sweaters/Hoodies: fleece material as a jacket",
        "expected_attributes": {"department_gender": "Women", "primary_material": "Fleece"},
        "expected_residual": ""
    },
    {
        "query": "sport coats for men big and tall",
        "category": "Jackets & Coats",
        "difficulty": "Borderline",
        "borderline_note": "Sport coat / blazer category classification",
        "expected_attributes": {"department_gender": "Men"},
        "expected_residual": "sport big and tall"
    },
    {
        "query": "32 degrees jackets for women",
        "category": "Jackets & Coats",
        "difficulty": "Brand_Specific",
        "borderline_note": "Brand: 32 degrees",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "32 degrees"
    },

    # =========================================================================
    # 2. HOODIES & SWEATSHIRTS (9 zapytań)
    # =========================================================================
    {
        "query": "hoodies for women",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "hood": "Yes"},
        "expected_residual": ""
    },
    {
        "query": "hoodies for men",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Men", "hood": "Yes"},
        "expected_residual": ""
    },
    {
        "query": "oversized sweatshirt for women",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "hood": "No"},
        "expected_residual": "oversized"
    },
    {
        "query": "california sweatshirt for women",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "hood": "No"},
        "expected_residual": "california"
    },
    {
        "query": "yellow champion hoodie",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"primary_color": "Yellow", "hood": "Yes"},
        "expected_residual": "champion"
    },
    {
        "query": "track jacket men venum",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Jackets: 'track jacket' is zip-up sportswear sweatshirt",
        "expected_attributes": {"department_gender": "Men", "closure_type": "Zip-up"},
        "expected_residual": "track venum"
    },
    {
        "query": "womens red zip up hoodie",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with light jacket: zip-up hoodie",
        "expected_attributes": {"department_gender": "Women", "primary_color": "Red", "hood": "Yes", "closure_type": "Zip-up"},
        "expected_residual": ""
    },
    {
        "query": "zipper sweaters for women without hoodie",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Sweaters: query says 'sweaters without hoodie' but means zip sweatshirt",
        "expected_attributes": {"department_gender": "Women", "hood": "No", "closure_type": "Zip-up"},
        "expected_residual": ""
    },
    {
        "query": "g star hoodies for men",
        "category": "Hoodies & Sweatshirts",
        "difficulty": "Brand_Specific",
        "borderline_note": "Brand: G-Star",
        "expected_attributes": {"department_gender": "Men", "hood": "Yes"},
        "expected_residual": "g star"
    },

    # =========================================================================
    # 3. SWEATERS & CARDIGANS (9 zapytań)
    # =========================================================================
    {
        "query": "womens sweaters",
        "category": "Sweaters & Cardigans",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": ""
    },
    {
        "query": "sweaters for women",
        "category": "Sweaters & Cardigans",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": ""
    },
    {
        "query": "cute fall sweaters",
        "category": "Sweaters & Cardigans",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {},
        "expected_residual": "cute fall"
    },
    {
        "query": "pink argyle sweater",
        "category": "Sweaters & Cardigans",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"primary_color": "Pink", "pattern": "Plaid / Checked"},
        "expected_residual": "argyle"
    },
    {
        "query": "women elegant sweater",
        "category": "Sweaters & Cardigans",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "elegant"
    },
    {
        "query": "3/4 sleeve cardigan for women",
        "category": "Sweaters & Cardigans",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Tops/Jackets: open-front cardigan",
        "expected_attributes": {"department_gender": "Women", "closure_type": "Button-up (Cardigan)"},
        "expected_residual": "3/4 sleeve"
    },
    {
        "query": "crop cardigan",
        "category": "Sweaters & Cardigans",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Crop Tops: cropped cardigan sweater",
        "expected_attributes": {"closure_type": "Button-up (Cardigan)"},
        "expected_residual": "crop"
    },
    {
        "query": "white cardigan chunky",
        "category": "Sweaters & Cardigans",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with light outerwear: chunky knit cardigan",
        "expected_attributes": {"primary_color": "White", "closure_type": "Button-up (Cardigan)"},
        "expected_residual": "chunky"
    },
    {
        "query": "port authority cardigan",
        "category": "Sweaters & Cardigans",
        "difficulty": "Brand_Specific",
        "borderline_note": "Brand: Port Authority",
        "expected_attributes": {"closure_type": "Button-up (Cardigan)"},
        "expected_residual": "port authority"
    },

    # =========================================================================
    # 4. SHIRTS & BLOUSES (9 zapytań)
    # =========================================================================
    {
        "query": "womens white button up blouse",
        "category": "Shirts & Blouses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "White", "closure_type": "Full Button Front"},
        "expected_residual": ""
    },
    {
        "query": "black mens dress shirt slim fit",
        "category": "Shirts & Blouses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Men", "primary_color": "Black", "collar": "Classic Collar"},
        "expected_residual": "dress slim fit"
    },
    {
        "query": "lemon yellow blouse",
        "category": "Shirts & Blouses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"primary_color": "Yellow"},
        "expected_residual": "lemon"
    },
    {
        "query": "mens linen shirt",
        "category": "Shirts & Blouses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Men", "primary_material": "Linen"},
        "expected_residual": ""
    },
    {
        "query": "white button down blouse women",
        "category": "Shirts & Blouses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "White", "closure_type": "Full Button Front"},
        "expected_residual": ""
    },
    {
        "query": "fleece lined flannel shirt women",
        "category": "Shirts & Blouses",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Jacket (shacket): fleece lined flannel shirt",
        "expected_attributes": {"department_gender": "Women", "pattern": "Plaid / Checked"},
        "expected_residual": "fleece lined flannel"
    },
    {
        "query": "wide sleeve flannel shirt women",
        "category": "Shirts & Blouses",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with casual tops: flannel shirt",
        "expected_attributes": {"department_gender": "Women", "pattern": "Plaid / Checked"},
        "expected_residual": "wide sleeve flannel"
    },
    {
        "query": "mens navy and gray oxford shirt",
        "category": "Shirts & Blouses",
        "difficulty": "Borderline",
        "borderline_note": "Classic woven Oxford button-down shirt",
        "expected_attributes": {"department_gender": "Men", "primary_color": "Navy", "collar": "Classic Collar"},
        "expected_residual": "gray oxford"
    },
    {
        "query": "4xlt dress shirts for men big and tall",
        "category": "Shirts & Blouses",
        "difficulty": "Brand_Specific",
        "borderline_note": "Sizing & Formal Wear: 4XLT dress shirt",
        "expected_attributes": {"department_gender": "Men", "collar": "Classic Collar"},
        "expected_residual": "4xlt dress big and tall"
    },

    # =========================================================================
    # 5. T-SHIRTS & TOPS (9 zapytań)
    # =========================================================================
    {
        "query": "jerzees long sleeve t shirt",
        "category": "T-Shirts & Tops",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"sleeve_length": "Long Sleeve"},
        "expected_residual": "jerzees"
    },
    {
        "query": "v neck white t shirt women",
        "category": "T-Shirts & Tops",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "White", "neckline": "V-Neck"},
        "expected_residual": ""
    },
    {
        "query": "brown tank top womens",
        "category": "T-Shirts & Tops",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "Brown", "sleeve_length": "Sleeveless / Tank Top"},
        "expected_residual": ""
    },
    {
        "query": "cut out tank tops for women",
        "category": "T-Shirts & Tops",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "sleeve_length": "Sleeveless / Tank Top"},
        "expected_residual": "cut out"
    },
    {
        "query": "tank top plus size women",
        "category": "T-Shirts & Tops",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "sleeve_length": "Sleeveless / Tank Top"},
        "expected_residual": "plus size"
    },
    {
        "query": "golf polo slim fit",
        "category": "T-Shirts & Tops",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Shirts: Polo has collar and buttons but is jersey knit top",
        "expected_attributes": {"closure_type": "Partial Button (Polo)", "collar": "Classic Collar"},
        "expected_residual": "golf slim fit"
    },
    {
        "query": "nautica polo shirts for men",
        "category": "T-Shirts & Tops",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Shirts: Polo shirt",
        "expected_attributes": {"department_gender": "Men", "closure_type": "Partial Button (Polo)"},
        "expected_residual": "nautica"
    },
    {
        "query": "mens cotton polo shirts with pockets and short sleeves",
        "category": "T-Shirts & Tops",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with Shirts: Polo with pocket and collar",
        "expected_attributes": {"department_gender": "Men", "primary_material": "Cotton", "sleeve_length": "Short Sleeve", "closure_type": "Partial Button (Polo)"},
        "expected_residual": "pockets"
    },
    {
        "query": "dewalt shirt for men",
        "category": "T-Shirts & Tops",
        "difficulty": "Brand_Specific",
        "borderline_note": "Brand: Dewalt graphic t-shirt",
        "expected_attributes": {"department_gender": "Men"},
        "expected_residual": "dewalt"
    },

    # =========================================================================
    # 6. PANTS & TROUSERS (9 zapytań)
    # =========================================================================
    {
        "query": "womens skinny jeans",
        "category": "Pants & Trousers",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "pant_type": "Jeans", "leg_fit": "Slim / Skinny", "primary_material": "Denim"},
        "expected_residual": ""
    },
    {
        "query": "trousers women",
        "category": "Pants & Trousers",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "pant_type": "Chinos / Trousers"},
        "expected_residual": ""
    },
    {
        "query": "plaid trousers for women",
        "category": "Pants & Trousers",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "pattern": "Plaid / Checked", "pant_type": "Chinos / Trousers"},
        "expected_residual": ""
    },
    {
        "query": "mens blue jeans regular fit",
        "category": "Pants & Trousers",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Men", "primary_color": "Blue", "pant_type": "Jeans", "primary_material": "Denim", "leg_fit": "Straight"},
        "expected_residual": "regular fit"
    },
    {
        "query": "black cargo pants women",
        "category": "Pants & Trousers",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "Black", "pant_type": "Cargo"},
        "expected_residual": ""
    },
    {
        "query": "womens sweatpants without pockets",
        "category": "Pants & Trousers",
        "difficulty": "Borderline",
        "borderline_note": "Sweatpants / Loungewear vs casual trousers",
        "expected_attributes": {"department_gender": "Women", "pant_type": "Sweatpants"},
        "expected_residual": "without pockets"
    },
    {
        "query": "mens shorts",
        "category": "Pants & Trousers",
        "difficulty": "Borderline",
        "borderline_note": "Shorts as lower body category member",
        "expected_attributes": {"department_gender": "Men", "length": "Shorts"},
        "expected_residual": ""
    },
    {
        "query": "women fleece sweatpants",
        "category": "Pants & Trousers",
        "difficulty": "Borderline",
        "borderline_note": "Fleece sweatpants",
        "expected_attributes": {"department_gender": "Women", "pant_type": "Sweatpants"},
        "expected_residual": "fleece"
    },
    {
        "query": "carhartt double front pants for men",
        "category": "Pants & Trousers",
        "difficulty": "Brand_Specific",
        "borderline_note": "Brand: Carhartt workwear pants",
        "expected_attributes": {"department_gender": "Men", "pant_type": "Chinos / Trousers"},
        "expected_residual": "carhartt double front"
    },

    # =========================================================================
    # 7. DRESSES (9 zapytań)
    # =========================================================================
    {
        "query": "womens dresses",
        "category": "Dresses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": ""
    },
    {
        "query": "dresses for women casual summer",
        "category": "Dresses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "casual summer"
    },
    {
        "query": "white dresses for women",
        "category": "Dresses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "White"},
        "expected_residual": ""
    },
    {
        "query": "party dress for women sexy elegant",
        "category": "Dresses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "party sexy elegant"
    },
    {
        "query": "black funeral dress",
        "category": "Dresses",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"primary_color": "Black"},
        "expected_residual": "funeral"
    },
    {
        "query": "women's striped short sleeve loose swing t-shirt dress",
        "category": "Dresses",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with T-shirts: 't-shirt dress' has T-shirt in name but is a Dress",
        "expected_attributes": {"department_gender": "Women", "pattern": "Striped", "sleeve_length": "Short Sleeve", "silhouette": "A-Line / Flared"},
        "expected_residual": "loose t-shirt dress"
    },
    {
        "query": "tank maxi dress summer",
        "category": "Dresses",
        "difficulty": "Borderline",
        "borderline_note": "Borderline with tank top: maxi tank dress",
        "expected_attributes": {"length": "Maxi", "sleeve_length": "Sleeveless / Straps"},
        "expected_residual": "summer"
    },
    {
        "query": "cami tiered dress",
        "category": "Dresses",
        "difficulty": "Borderline",
        "borderline_note": "Cami straps tiered dress",
        "expected_attributes": {"sleeve_length": "Sleeveless / Straps"},
        "expected_residual": "tiered"
    },
    {
        "query": "dresses for women party wedding",
        "category": "Dresses",
        "difficulty": "Brand_Specific",
        "borderline_note": "Occasion-rich query: party wedding",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "party wedding"
    },

    # =========================================================================
    # 8. FOOTWEAR (9 zapytań)
    # =========================================================================
    {
        "query": "shoes for women",
        "category": "Footwear",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women"},
        "expected_residual": "shoes"
    },
    {
        "query": "shoes for men",
        "category": "Footwear",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Men"},
        "expected_residual": "shoes"
    },
    {
        "query": "boots for women",
        "category": "Footwear",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "shaft_height": "Mid (ankle boot)"},
        "expected_residual": ""
    },
    {
        "query": "heel boots for women",
        "category": "Footwear",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "heel_sole_type": "Stiletto / High Heel"},
        "expected_residual": ""
    },
    {
        "query": "black slip on sneakers for women",
        "category": "Footwear",
        "difficulty": "Standard",
        "borderline_note": "",
        "expected_attributes": {"department_gender": "Women", "primary_color": "Black", "shaft_height": "Low (below ankle / sneakers)", "fastening": "Slip-on"},
        "expected_residual": "sneakers"
    },
    {
        "query": "water shoes",
        "category": "Footwear",
        "difficulty": "Borderline",
        "borderline_note": "Borderline aquatic/sport shoes",
        "expected_attributes": {"shaft_height": "Low (below ankle / sneakers)"},
        "expected_residual": "water"
    },
    {
        "query": "cap toe brown shoes",
        "category": "Footwear",
        "difficulty": "Borderline",
        "borderline_note": "Formal oxford shoes with cap toe styling",
        "expected_attributes": {"primary_color": "Brown"},
        "expected_residual": "cap toe"
    },
    {
        "query": "cowboy boots women",
        "category": "Footwear",
        "difficulty": "Borderline",
        "borderline_note": "Western boots with mid/high shaft",
        "expected_attributes": {"department_gender": "Women", "shaft_height": "High (knee-high / tall boot)"},
        "expected_residual": "cowboy"
    },
    {
        "query": "adidas shoes men",
        "category": "Footwear",
        "difficulty": "Brand_Specific",
        "borderline_note": "Brand: Adidas sneakers",
        "expected_attributes": {"department_gender": "Men"},
        "expected_residual": "adidas"
    },

    # =========================================================================
    # 9. NONE / OUT OF SCOPE (8 zapytań)
    # =========================================================================
    {
        "query": "ratchet belts for men without buckle",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Accessories: belt",
        "expected_attributes": {},
        "expected_residual": "ratchet belts for men without buckle"
    },
    {
        "query": "mens belt without buckle leather",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Accessories: leather belt",
        "expected_attributes": {},
        "expected_residual": "mens belt without buckle leather"
    },
    {
        "query": "leather belts for men",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Accessories: leather belts",
        "expected_attributes": {},
        "expected_residual": "leather belts for men"
    },
    {
        "query": "compression socks women",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Hosiery / medical socks",
        "expected_attributes": {},
        "expected_residual": "compression socks women"
    },
    {
        "query": "wool socks",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Hosiery: socks",
        "expected_attributes": {},
        "expected_residual": "wool socks"
    },
    {
        "query": "curious george yellow hat",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Headwear / costume hat",
        "expected_attributes": {},
        "expected_residual": "curious george yellow hat"
    },
    {
        "query": "plain black fitted hats for men",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Headwear / baseball cap",
        "expected_attributes": {},
        "expected_residual": "plain black fitted hats for men"
    },
    {
        "query": "thick belts for women",
        "category": "None",
        "difficulty": "Out_of_Scope",
        "borderline_note": "Accessories: belt",
        "expected_attributes": {},
        "expected_residual": "thick belts for women"
    }
]

# Zapisujemy do CSV
OUTPUT_FILE = "fashion_test_benchmark.csv"
fieldnames = ["query_id", "query", "category", "difficulty", "borderline_note", "expected_attributes", "expected_residual"]

# Mapujemy Query_ID z clothing_queries.csv
with open("clothing_queries.csv", "r", encoding="utf-8") as f:
    lookup = {row["Query_Text"].strip().lower(): row["Query_ID"] for row in csv.DictReader(f)}

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in BENCHMARK_DATA:
        q_norm = row["query"].strip().lower()
        qid = lookup.get(q_norm, "UNKNOWN")
        writer.writerow({
            "query_id": qid,
            "query": row["query"],
            "category": row["category"],
            "difficulty": row["difficulty"],
            "borderline_note": row["borderline_note"],
            "expected_attributes": json.dumps(row["expected_attributes"]),
            "expected_residual": row["expected_residual"]
        })

print(f"Pomyślnie wygenerowano plik: {OUTPUT_FILE} ({len(BENCHMARK_DATA)} wierszy).")
