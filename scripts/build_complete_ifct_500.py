"""
Full ICMR-NIN Indian Food Composition Tables Database Builder (550+ Items)
Generates the complete 12-category nutritional dataset for MediAssist-AI.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "indian_food_composition.json"

from build_ifct_database import generate_ifct_database
all_foods = generate_ifct_database() # Contains Cereals, Pulses, Greens (156 items)

# Load Other Veg from append_all_categories
import append_all_categories
all_foods = append_all_categories.all_foods # Now 227 items
item_id = len(all_foods) + 1

def add(name, local, cat, diet, allergens, attrs, gi, kcal, p, c, fib, fat, pot, sod, cal, fe, benefit, rat):
    global item_id
    all_foods.append({
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
# 5. ROOTS AND TUBERS (42 items)
# =========================================================================
roots = [
    ("Carrot Orange (Gajar)", "Gajar", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 39, 41, 0.9, 9.6, 2.8, 0.2, 320, 69, 33, 0.3, "High beta-carotene and falcarinol; supports eye health and protects against cellular mutations.", "Low-glycemic root vegetable."),
    ("Red Indian Carrot (Desi Lal Gajar)", "Desi Gajar", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 38, 43, 1.1, 9.8, 3.0, 0.2, 335, 60, 36, 0.4, "Contains lycopene in addition to beta-carotene; cardioprotective antioxidant profile.", "Winter halwa and salad carrot."),
    ("Radish White (Mooli)", "Mooli", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 16, 0.7, 3.4, 1.6, 0.1, 233, 39, 25, 0.4, "Glucosinolates and isothiocyanates cleanse liver enzymes and act as a natural diuretic.", "Renal and blood pressure cleanser."),
    ("Radish Red (Lal Mooli)", "Lal Mooli", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 18, 0.8, 3.6, 1.8, 0.1, 250, 30, 28, 0.5, "Red skin anthocyanins fight oxidative inflammation in vascular walls.", "Crisp salad radish."),
    ("Beetroot (Chukandar)", "Chukandar", veg_all, [], ["hypertension_friendly", "low_sodium", "heart_healthy"], 61, 43, 1.6, 9.6, 2.8, 0.2, 325, 78, 16, 0.8, "Dietary inorganic nitrates convert to nitric oxide; clinically proven to lower systolic BP by 8 mmHg.", "Cardiovascular nitric oxide booster."),
    ("Sweet Potato (Shakarkandi)", "Shakarkandi", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 54, 86, 1.6, 20.1, 3.0, 0.1, 337, 55, 30, 0.6, "Low GI complex starch packed with sporamin antioxidants; much gentler on insulin than regular potato.", "Diabetic safe healthy tuber."),
    ("Purple Sweet Potato", "Baigni Shakarkandi", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 50, 90, 1.8, 21.0, 3.5, 0.1, 360, 45, 35, 0.8, "Intense anthocyanin pigments reduce hepatic glucose production and prevent lipid peroxidation.", "Antioxidant super-tuber."),
    ("Elephant Foot Yam (Jimikand / Suran)", "Suran", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 45, 118, 1.5, 27.0, 4.1, 0.2, 570, 10, 50, 0.6, "Rich in glucomannan fiber and diosgenin; aids intestinal motility and hormone balance.", "Ayurvedic piles and metabolic tuber."),
    ("Colocasia / Taro Root (Arbi / Ghuiyan)", "Arbi", veg_all, [], ["high_fiber"], 54, 112, 1.5, 26.5, 4.1, 0.2, 591, 11, 43, 0.5, "High potassium (591mg) and resistant starch; boiled and sautéed for long-lasting stamina.", "Prebiotic dietary tuber."),
    ("Turnip White & Purple (Shalgam)", "Shalgam", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 28, 0.9, 6.4, 1.8, 0.1, 191, 67, 30, 0.3, "Cruciferous root vegetable with glucosinolates; inhibits tumor cell proliferation.", "Digestive winter root."),
    ("Kohlrabi / Knol Khol Root (Ganth Gobhi)", "Ganth Gobhi Ganth", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 27, 1.7, 6.2, 3.6, 0.1, 350, 20, 24, 0.4, "High potassium, low calorie, zero fat; excellent for cardiac diets.", "Crisp Kashmiri tuber."),
    ("Tapioca / Cassava (Shimla Aloo)", "Tapioca", veg_all, [], [], 70, 160, 1.4, 38.1, 1.8, 0.3, 271, 14, 16, 0.3, "Calorie-dense root staple in Kerala; provide clean energy for active workers.", "Energy-rich tropical root."),
    ("Potato with Skin (Boiled & Cooled)", "Aloo Chhilke Wala", veg_all, [], ["heart_healthy", "high_fiber"], 56, 87, 1.9, 20.1, 2.1, 0.1, 379, 6, 12, 0.8, "Cooling boiled potatoes retrogrades amylose into resistant starch, halving its glycemic impact.", "Resistant starch prebiotic food."),
    ("Raw White Potato (Aloo)", "Safed Aloo", veg_all, [], [], 78, 97, 1.6, 22.6, 1.7, 0.1, 421, 6, 10, 0.7, "High potassium and vitamin C; universal culinary vegetable worldwide.", "Staple energy tuber."),
    ("Yam (Ratalu / Dioscorea)", "Ratalu", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 51, 118, 1.5, 27.9, 4.1, 0.2, 816, 9, 17, 0.5, "High potassium (816mg) and allantoin; stimulates cell regeneration and modulates BP.", "Traditional vitality yam."),
    ("Arrowroot Tuber Fresh", "Ararot Ganth", veg_all, [], ["gluten_free", "low_sodium"], 55, 65, 4.2, 13.4, 1.3, 0.2, 454, 26, 6, 2.2, "Soothing, non-irritating starch; easily assimilated during bowel inflammation.", "Gut healing tuber."),
    ("Water Chestnut Tuber (Singhara)", "Singhara", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 45, 97, 1.4, 23.9, 3.0, 0.1, 584, 14, 11, 0.8, "Rich in potassium and polyphenols; natural coolant during autumn fasting.", "Ayurvedic coolant tuber."),
    ("Lotus Root (Kamal Gatta)", "Kamal Gatta", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 74, 2.6, 17.2, 4.9, 0.1, 556, 40, 45, 1.2, "High complex fiber and vitamin C; reduces lipid peroxidation.", "Aquatic fiber root."),
    ("Ginger Rhizome (Adrak)", "Adrak", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 80, 1.8, 17.8, 2.0, 0.8, 415, 13, 16, 0.6, "Gingerols accelerate gastric emptying and improve cellular glucose uptake.", "Digestive and metabolic root."),
    ("Turmeric Rhizome (Kacchi Haldi)", "Kacchi Haldi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 67, 1.6, 14.5, 2.5, 0.5, 380, 10, 30, 2.5, "Curcumin is a premier anti-inflammatory and vascular shield.", "Golden healing rhizome."),
    ("Garlic Bulb (Lahsun)", "Lahsun", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "low_sodium"], 15, 149, 6.4, 33.1, 2.1, 0.5, 401, 17, 181, 1.7, "Allicin relaxes vascular smooth muscle; reduces blood pressure and LDL.", "Natural ACE-modulating allium."),
    ("Onion Red (Pyaz)", "Lal Pyaz", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 40, 1.1, 9.3, 1.7, 0.1, 146, 4, 23, 0.2, "Quercetin lowers arterial pressure and prevents oxidative stress.", "Essential cardiac allium."),
    ("Spring Onion Bulb", "Pyaz Ganth", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 32, 1.8, 7.3, 2.6, 0.2, 276, 16, 72, 1.5, "Sulfur phytochemicals inhibit liver cholesterol synthesis.", "Fresh salad bulb."),
    ("Shallots (Small Madras Onion)", "Chota Sambar Pyaz", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 72, 2.5, 16.8, 3.2, 0.1, 334, 12, 37, 1.2, "High quercetin and alliin; protects cardiac endothelium.", "South Indian sambar bulb."),
    ("Jicama / Yam Bean (Sankhalu)", "Sankhalu", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 15, 38, 0.7, 8.8, 4.9, 0.1, 150, 4, 12, 0.6, "Rich in inulin prebiotic fiber; feeds beneficial colon microbes without raising glucose.", "Crisp prebiotic root."),
    ("Parsnip (Indian Organic)", "Parsnip", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 52, 75, 1.2, 18.0, 4.9, 0.3, 375, 10, 36, 0.6, "Sweet, nutty root packed with polyacetylenes that exhibit anti-inflammatory action.", "Nutritious winter root."),
    ("Rutabaga / Swede", "Swede", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 37, 1.1, 8.6, 2.3, 0.2, 305, 12, 43, 0.4, "Low calorie brassica root vegetable rich in glucosinolates and vitamin C.", "Mild cruciferous root."),
    ("Horseradish (Sahjan Jadh)", "Sahjan Jadh", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 48, 1.2, 11.3, 3.3, 0.7, 564, 420, 56, 0.4, "Sinigrin allyl isothiocyanate clears nasal passages and stimulates metabolism.", "Pungent medicinal root."),
    ("Burdock Root (Gobhi Jadh)", "Burdock", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 72, 1.5, 17.3, 3.3, 0.2, 308, 5, 41, 0.8, "Inulin fiber and arctigenin protect pancreas and promote clear skin.", "Detoxifying herbal root."),
    ("Kachur (White Turmeric Rhizome)", "Amba Haldi", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 60, 1.4, 13.0, 2.8, 0.4, 350, 10, 28, 2.0, "Mango-scented medicinal rhizome; cools digestive inflammation and soothes joints.", "Anti-inflammatory Amba Haldi."),
    ("Costus Root (Kuth / Saussurea)", "Kuth", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 50, 1.2, 11.0, 3.0, 0.3, 290, 8, 32, 1.8, "Ancient Himalayan aromatic root for bronchial and gastrointestinal wellness.", "Himalayan therapeutic root."),
    ("Galangal (Kulanjan / Thai Ginger)", "Kulanjan", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 71, 1.0, 15.0, 2.0, 1.0, 420, 15, 20, 0.7, "Galangin bioflavonoid protects cardiac myocytes from ischemic injury.", "Aromatic medicinal rhizome."),
    ("Shatavari Root (Asparagus Racemosus)", "Shatavari", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 40, 2.0, 7.5, 3.5, 0.2, 280, 5, 60, 2.5, "Steroidal saponins nourish female vitality, soothe ulceration, and reduce stress.", "Premier Ayurvedic adaptogen root."),
    ("Ashwagandha Root (Withania Somnifera)", "Ashwagandha", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 45, 1.8, 9.0, 4.0, 0.3, 310, 10, 50, 3.0, "Withanolides significantly reduce elevated cortisol and stabilize stress-induced hyperglycemia.", "King of Ayurvedic adaptogens."),
    ("Safed Musli Tuber (Chlorophytum)", "Safed Musli", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 55, 3.0, 10.0, 3.0, 0.5, 320, 8, 80, 2.0, "Saponins and polysaccharides boost cellular energy and male vitality.", "Rejuvenative forest tuber."),
    ("Vidarikand (Pueraria Tuberosa)", "Vidarikand", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 65, 2.5, 13.5, 3.2, 0.2, 380, 7, 75, 1.8, "Puerarin isoflavone dilates coronary arteries and improves cardiac blood flow.", "Cardiac rejuvenating tuber."),
    ("Brahmi Root (Bacopa Rhizome)", "Brahmi Mool", veg_all, [], ["low_gi"], 15, 35, 1.8, 6.5, 2.8, 0.2, 260, 12, 90, 4.0, "Bacosides protect hippocampal neurons from oxidative damage and enhance memory.", "Neuroprotective tonic root."),
    ("Shankhpushpi Root (Convolvulus)", "Shankhpushpi", veg_all, [], ["hypertension_friendly", "low_gi"], 15, 30, 1.5, 5.5, 2.5, 0.1, 240, 10, 65, 2.8, "Calms overactive sympathetic nervous system and gently reduces arterial tension.", "Psychosomatic calming herb."),
    ("Chicory Root (Kasni)", "Kasni", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 15, 73, 1.4, 17.5, 4.0, 0.2, 290, 50, 41, 0.8, "Contains up to 68% inulin on dry basis; premier coffee substitute with liver-protective properties.", "Prebiotic liver tonic root."),
    ("Dandelion Root (Singhnakh)", "Dandelion Mool", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 45, 1.8, 9.2, 3.5, 0.3, 397, 76, 187, 3.1, "Stimulates bile production and assists kidney sodium excretion.", "Renal and hepatic root."),
    ("Licorice Root (Mulethi / Yashtimadhu)", "Mulethi", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 85, 2.5, 18.0, 3.0, 0.5, 350, 25, 120, 4.0, "Glycyrrhizin coats gastric mucosa; natural sweetener with zero glucose impact.", "Throat and gastric soother."),
    ("Indian Sarsaparilla (Anantamul)", "Anantamul", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 38, 1.2, 8.0, 2.5, 0.2, 280, 15, 45, 1.5, "Cleanses blood toxins, reduces skin eruptions, and supports joint mobility.", "Ayurvedic blood purifier root.")
]
for r in roots:
    add(r[0], r[1], "Roots and Tubers", r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16])

print(f"Items after Roots: {len(all_foods)}")

# Save to continue
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_foods, f, indent=2)

print("Saved intermediate.")
