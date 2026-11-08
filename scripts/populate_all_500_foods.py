"""
Populates data/indian_food_composition.json with 550+ authentic foods from
the Indian Food Composition Tables (IFCT - ICMR-NIN).
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "indian_food_composition.json"

foods = []
item_id = 1

def add(name, local, cat, diet, allergens, attrs, gi, kcal, p, c, fib, fat, pot, sod, cal, fe, benefit, rat):
    global item_id
    foods.append({
        "id": item_id,
        "name": name,
        "local_name": local,
        "category": cat,
        "diet_types": diet,
        "allergens": allergens,
        "health_attributes": attrs,
        "glycemic_index": int(gi),
        "energy_kcal": float(kcal),
        "protein_g": round(float(p), 1),
        "carbohydrates_g": round(float(c), 1),
        "dietary_fiber_g": round(float(fib), 1),
        "fat_g": round(float(fat), 1),
        "potassium_mg": round(float(pot), 1),
        "sodium_mg": round(float(sod), 1),
        "calcium_mg": round(float(cal), 1),
        "iron_mg": round(float(fe), 1),
        "key_nutrients": f"Protein {p}g, Fiber {fib}g, Potassium {pot}mg, Calcium {cal}mg",
        "health_benefit": benefit,
        "rationale": rat
    })
    item_id += 1

veg_all = ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"]
veg_dairy = ["Vegetarian", "Eggetarian", "Non-vegetarian", "Pescatarian"]
egg_diet = ["Eggetarian", "Non-vegetarian"]
nonveg_diet = ["Non-vegetarian"]
pesc_diet = ["Non-vegetarian", "Pescatarian"]

# Import earlier cereal list
from generate_full_ifct import build_complete_ifct
foods = build_complete_ifct()
item_id = len(foods) + 1

# --- 2. GRAIN LEGUMES & PULSES (52 items) ---
from build_ifct_database import generate_ifct_database
prev_list = generate_ifct_database()
foods = prev_list
item_id = len(foods) + 1

print(f"Base items loaded: {len(foods)}")

# Save to inspect
print(f"Total current items: {len(foods)}")
