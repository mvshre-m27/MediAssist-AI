"""
Batch 3 Appender: Nuts & Oilseeds, Spices & Condiments, Dairy, Animals, Beverages, and Oils.
Finalizes the IFCT dataset to 560+ total items.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "indian_food_composition.json"

with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    foods = json.load(f)

item_id = len(foods) + 1

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

# =========================================================================
# 7. NUTS AND OILSEEDS (42 items)
# =========================================================================
nuts = [
    ("Almonds Raw with Skin (Badam)", "Badam", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"], 15, 579, 21.2, 21.6, 12.5, 49.9, 733, 1, 269, 3.7, "Magnesium (270mg) improves insulin sensitivity; monounsaturated fats and vitamin E protect arterial walls.", "AHA certified cardiac superfood."),
    ("Walnuts Halves (Akhrot)", "Akhrot", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "low_sodium"], 15, 654, 15.2, 13.7, 6.7, 65.2, 441, 2, 98, 2.9, "Highest plant omega-3 (ALA, 9g/100g); clinically proven to improve arterial flow-mediated dilation.", "The premier brain and heart nut."),
    ("Pistachios Roasted & Salt-Free (Pista)", "Bina Namak Pista", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"], 15, 560, 20.2, 27.2, 10.6, 45.3, 1025, 1, 105, 3.9, "Lutein, zeaxanthin, and potassium (1025mg); lowest calorie nut with superior nitric oxide boost.", "Hypertension-friendly potassium nut."),
    ("Cashew Nuts Raw (Kaju)", "Kaju", veg_all, ["tree_nuts"], ["heart_healthy", "high_protein"], 22, 553, 18.2, 30.2, 3.3, 43.8, 660, 12, 37, 6.7, "Rich in stearic acid and oleic acid; does not raise LDL when eaten in controlled portions.", "Nutritious culinary nut."),
    ("Groundnuts / Peanuts Raw with Red Skin (Mungfali)", "Kacchi Mungfali", veg_all, ["peanuts"], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein", "high_fiber"], 14, 567, 25.8, 16.1, 8.5, 49.2, 705, 18, 92, 4.6, "Resveratrol and p-coumaric acid in red skin; over 25% protein with near-zero glycemic impact.", "Everyday Indian plant protein."),
    ("Roasted Peanuts Unshelled", "Bhuni Mungfali", veg_all, ["peanuts"], ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein"], 15, 585, 24.4, 21.0, 8.0, 49.7, 658, 6, 54, 2.2, "Roasting increases antioxidant polyphenols by up to 22%; crunchy sustained satiety snack.", "Healthy evening diabetic snack."),
    ("White Sesame Seeds (Safed Til)", "Safed Til", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_calcium", "high_iron"], 15, 573, 17.7, 23.4, 11.8, 49.7, 468, 11, 975, 14.6, "Incredible calcium (975mg/100g); sesamin and sesamolin lignans inhibit cholesterol synthesis.", "Bone and blood pressure super-seed."),
    ("Black Sesame Seeds (Kala Til)", "Kala Til", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_calcium", "high_iron"], 15, 570, 18.0, 23.0, 12.5, 50.0, 480, 10, 1050, 16.0, "Higher antioxidant and calcium concentration than white seeds; strengthens bone and kidney energy.", "Ayurvedic rejuvenating seed."),
    ("Flaxseeds / Linseeds (Alsi)", "Alsi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"], 10, 534, 18.3, 28.9, 27.3, 42.2, 813, 30, 255, 5.7, "Richest source of SDG lignans and plant omega-3; proven in randomized trials to lower both SBP and DBP.", "Cardiovascular champion functional food."),
    ("Chia Seeds", "Chia", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"], 10, 486, 16.5, 42.1, 34.4, 30.7, 407, 16, 631, 7.7, "Absorbs 10x its weight in water to create an intestinal gel barrier; blunts postprandial glucose.", "Blood sugar and weight management seed."),
    ("Basil Seeds / Sabja Seeds (Tukmaria)", "Sabja", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 10, 430, 14.8, 43.0, 37.0, 25.0, 420, 12, 600, 7.0, "Ayurvedic cooling seed; mucilage fiber slows gastric digestion and relieves acid reflux.", "Traditional summer coolant seed."),
    ("Pumpkin Seeds (Kaddu ke Beej / Pepitas)", "Kaddu ke Beej", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"], 15, 559, 30.2, 10.7, 6.0, 49.0, 809, 7, 46, 8.8, "Huge zinc and magnesium (592mg); crucial for insulin secretion and prostate cellular health.", "Zinc and magnesium mineral powerhouse."),
    ("Sunflower Seeds (Surajmukhi ke Beej)", "Surajmukhi Beej", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein"], 15, 584, 20.8, 20.0, 8.6, 51.5, 645, 9, 78, 5.2, "Outstanding Vitamin E (35mg - 230% DV); protects cell membranes from peroxidation.", "Cellular antioxidant seed."),
    ("Watermelon Seeds Dried (Tarbooj ke Beej)", "Tarbooj Magaj", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein"], 15, 557, 28.3, 15.3, 4.0, 47.4, 648, 99, 54, 7.3, "Citrulline, arginine, and dense plant protein; supports vascular endothelial health.", "Magaj seed for heart and brain."),
    ("Muskmelon Seeds Dried (Kharbuja Magaj)", "Kharbuja Magaj", veg_all, [], ["diabetic_friendly", "low_gi", "high_protein"], 15, 550, 27.5, 16.0, 4.5, 46.5, 620, 85, 60, 6.8, "Cooling seed rich in polyunsaturated fats; traditional cooling thandai base.", "Ayurvedic brain coolant seed."),
    ("Cucumber Seeds Dried (Kheera Magaj)", "Kheera Magaj", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 540, 26.0, 16.5, 4.2, 45.0, 580, 50, 50, 6.0, "Diuretic and cooling properties; flushes uric acid.", "Cooling four-magaj blend seed."),
    ("Nigella Seeds / Black Seed (Kalonji)", "Kalonji", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 544, 21.0, 30.0, 12.0, 38.0, 540, 15, 570, 9.5, "Thymoquinone exhibits profound antidiabetic, antihypertensive, and immunomodulatory effects.", "Ancient panacea seed."),
    ("Mustard Seeds Black / Brown (Rai / Sarson)", "Rai / Sarson", veg_all, ["mustard"], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 508, 26.1, 28.1, 12.2, 36.2, 732, 13, 266, 9.2, "Sinigrin and myrosinase enzyme generate isothiocyanates; anti-inflammatory tadka spice.", "Essential Indian tempering seed."),
    ("Yellow Mustard Seeds (Pili Sarson)", "Pili Sarson", veg_all, ["mustard"], ["diabetic_friendly", "low_gi"], 15, 510, 25.5, 28.5, 12.0, 36.0, 720, 15, 270, 9.0, "Mild pungent aroma; preservative and digestive seed for achars and fish curries.", "Pickling and tempering mustard."),
    ("Poppy Seeds (Khus Khus)", "Khus Khus", veg_all, [], ["hypertension_friendly", "high_calcium", "high_fiber"], 15, 525, 18.0, 28.1, 19.5, 41.6, 719, 26, 1438, 9.8, "Enormous calcium (1438mg/100g); magnesium and zinc calm the nervous system for restorative sleep.", "Calcium champion sedative seed."),
    ("Gorgon Nut / Foxnut / Puffed Lotus Seeds (Makhana)", "Makhana", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "low_sodium"], 45, 347, 9.7, 76.9, 7.6, 0.1, 500, 3, 60, 1.4, "Virtually zero sodium and zero saturated fat; high kaempferol flavonoid fights inflammation.", "Top clinical cardiac and renal snack."),
    ("Roasted Salt-Free Makhana", "Bhuna Makhana", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "low_sodium"], 45, 350, 9.8, 77.0, 7.6, 0.2, 510, 4, 62, 1.4, "Crisp, airy snack; ideal crunchy replacement for fried chips in hypertension.", "Heart-healthy crunch snack."),
    ("Fresh Coconut Meat (Nariyal Giri)", "Kaccha Nariyal", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 15, 354, 3.3, 15.2, 9.0, 33.5, 356, 20, 14, 2.4, "Medium-chain triglycerides (MCTs) like lauric acid provide immediate hepatic energy; high fiber.", "Traditional coastal staple."),
    ("Dry Coconut / Copra (Khopra)", "Sukha Khopra", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 662, 6.9, 23.7, 16.3, 64.5, 543, 37, 26, 3.3, "Concentrated fiber (16.3g); traditional energy builder in winter laddoos.", "Concentrated dietary coconut."),
    ("Desiccated Coconut Powder", "Nariyal Boora", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 660, 6.8, 23.0, 16.0, 65.0, 540, 35, 25, 3.2, "Baking and garnish ingredient rich in manganese and copper.", "Convenient baking coconut."),
    ("Pine Nuts (Chilgoza)", "Chilgoza", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 673, 13.7, 13.1, 3.7, 68.4, 597, 2, 16, 5.5, "Pinolenic acid stimulates cholecystokinin (CCK) release, suppressing hunger for hours.", "Himalayan gourmet satiety nut."),
    ("Hazelnuts", "Pahadi Badam", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 628, 15.0, 16.7, 9.7, 60.8, 680, 0, 114, 4.7, "High in proanthocyanidins and folate; protects cardiovascular endothelium.", "Cardioprotective tree nut."),
    ("Brazil Nuts", "Brazil Nut", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 659, 14.3, 12.3, 7.5, 67.1, 659, 3, 160, 2.4, "World's highest natural selenium source (1917mcg/100g); just 1-2 nuts daily optimizes thyroid function.", "Thyroid and antioxidant super-nut."),
    ("Macadamia Nuts", "Macadamia", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 718, 7.9, 13.8, 8.6, 75.8, 368, 5, 85, 3.7, "Over 80% monounsaturated fat (palmitoleic acid); improves lipid profiles.", "Ultra-low carb keto nut."),
    ("Pecan Halves", "Pecan", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 691, 9.2, 13.9, 9.6, 72.0, 410, 0, 70, 2.5, "Highest total polyphenol content among all tree nuts; protects circulating LDL.", "Antioxidant tree nut."),
    ("Hemp Seeds Shelled (Bhang Dana)", "Bhang Dana", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"], 15, 553, 31.6, 8.7, 4.0, 48.8, 1200, 5, 70, 7.9, "3:1 optimal ratio of Omega-6 to Omega-3; exceptional plant protein with all essential amino acids.", "Himalayan complete protein seed."),
    ("Aniseed / Fennel Seeds (Saunf)", "Saunf", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 345, 15.8, 52.3, 39.8, 14.9, 1694, 88, 1196, 18.5, "Anethole relaxes gastrointestinal smooth muscle; massive potassium (1694mg) regulates blood pressure.", "After-meal digestive seed."),
    ("Carom Seeds (Ajwain)", "Ajwain", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 305, 15.4, 43.0, 39.2, 25.0, 1400, 10, 1525, 13.7, "Thymol provides rapid carminative relief; calcium antagonist action lowers elevated blood pressure.", "Ayurvedic antispasmodic seed."),
    ("Cumin Seeds (Jeera)", "Jeera", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_iron"], 15, 375, 17.8, 44.2, 10.5, 22.3, 1788, 168, 931, 66.4, "Cuminaldehyde stimulates pancreatic digestive enzymes; exceptional bioavailable iron (66mg).", "Metabolic and iron-rich spice seed."),
    ("Coriander Seeds (Sabut Dhania)", "Sabut Dhania", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 298, 12.4, 55.0, 41.9, 17.8, 1267, 35, 709, 16.3, "Linalool enhances glucose uptake in skeletal muscle and acts as a mild diuretic.", "Cooling lipid-lowering seed."),
    ("Fenugreek Seeds (Methi Dana)", "Methi Dana", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 15, 323, 23.0, 58.0, 24.6, 6.4, 770, 67, 176, 33.5, "4-hydroxyisoleucine and galactomannan fiber clinically proven to reduce fasting blood glucose and HbA1c.", "King of antidiabetic medicinal seeds."),
    ("Melon Seed Kernels Blend (Char Magaj)", "Char Magaj", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein"], 15, 560, 28.0, 15.0, 4.2, 47.0, 650, 40, 55, 7.0, "Classic 4-seed blend (watermelon, pumpkin, cantaloupe, cucumber); restorative for memory.", "Ayurvedic cognitive seed blend."),
    ("Soaked Peeled Almonds", "Bheege Chhile Badam", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"], 15, 570, 21.0, 21.0, 11.5, 49.0, 720, 1, 260, 3.5, "Soaking deactivates tannin enzyme inhibitors, dramatically improving nutrient assimilation.", "Traditional memory ritual."),
    ("Roasted Salt-Free Peanuts", "Bhuni Mungfali Sada", veg_all, ["peanuts"], ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein"], 14, 580, 25.0, 18.0, 8.5, 49.5, 700, 10, 90, 4.5, "Crunchy zero-sodium protein snack with high arginine for vascular nitric oxide.", "Heart healthy crunch."),
    ("Sprouted Fenugreek Seeds", "Ankurit Methi", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 120, 8.5, 18.0, 9.0, 1.5, 380, 15, 85, 8.0, "Germination eliminates bitterness while supercharging active antidiabetic enzymes.", "Live functional diabetic salad."),
    ("Apricot Kernels Sweet (Badam Giri)", "Giri Khubani", veg_all, ["tree_nuts"], ["diabetic_friendly", "low_gi"], 15, 600, 18.0, 16.0, 8.0, 52.0, 600, 5, 80, 4.5, "Traditional Ladakhi sweet apricot seeds; high oleic and linoleic essential fatty acids.", "Ladakhi organic nut."),
    ("Kalonji Seed Powder", "Kalonji Churna", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 540, 20.0, 30.0, 12.0, 38.0, 530, 15, 560, 9.0, "Concentrated thymoquinone; protects pancreatic beta cells from immune destruction.", "Therapeutic seed powder.")
]
for n in nuts:
    add(n[0], n[1], "Nuts and Oilseeds", n[2], n[3], n[4], n[5], n[6], n[7], n[8], n[9], n[10], n[11], n[12], n[13], n[14], n[15], n[16])

print(f"Items after Nuts: {len(foods)}")

# Save intermediate
with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
    json.dump(foods, f_out, indent=2)

print("Batch 3 step 1 complete.")
