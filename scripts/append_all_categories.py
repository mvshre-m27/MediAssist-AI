"""
Appends Other Vegetables, Roots & Tubers, Fruits, Nuts, Spices, Dairy, Meats, Beverages, and Oils
to reach 550+ total IFCT entries in data/indian_food_composition.json.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "indian_food_composition.json"

from build_ifct_database import generate_ifct_database
all_foods = generate_ifct_database() # Contains Cereals, Pulses, Greens (156 items)
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
# 4. OTHER VEGETABLES (75 items)
# =========================================================================
other_veg = [
    ("Bitter Gourd (Karela)", "Karela", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 17, 1.0, 3.7, 2.8, 0.2, 296, 5, 19, 0.4, "Contains charantin, vicine, and polypeptide-p; acts as a natural insulin secretagogue and mimics insulin action.", "Clinically validated antidiabetic vegetable."),
    ("Bottle Gourd (Lauki / Ghiya)", "Lauki", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 14, 0.6, 2.5, 2.0, 0.1, 150, 2, 26, 0.3, "96% water content and high potassium; gently lowers blood pressure and relieves water retention.", "Universal cooling and cardiac vegetable."),
    ("Ridge Gourd (Turai / Torai)", "Turai", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 16, 0.8, 3.4, 2.5, 0.2, 139, 3, 18, 0.4, "Rich in dietary cellulose and peptides that inhibit gluconeogenesis.", "Digestive and diabetic friendly."),
    ("Snake Gourd (Chichinda / Padwal)", "Padwal", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 18, 0.6, 3.3, 2.1, 0.3, 130, 4, 26, 0.3, "Mild natural diuretic and febrifuge; supports cardiac blood flow.", "Traditional Ayurvedic gourd."),
    ("Sponge Gourd (Nenua / Gilki)", "Gilki", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 15, 0.7, 3.1, 2.0, 0.2, 145, 3, 20, 0.4, "Light on stomach, low in calories, and zero cholesterol.", "Gentle everyday vegetable."),
    ("Ash Gourd / Winter Melon (Petha)", "Safed Petha", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 13, 0.4, 2.0, 2.9, 0.1, 111, 2, 30, 0.4, "Highly alkaline vegetable; neutralizes systemic acidity and clears cellular toxins.", "Renal and metabolic detoxifier."),
    ("Pointed Gourd (Parwal / Potala)", "Parwal", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 20, 2.0, 2.2, 3.0, 0.3, 214, 2, 30, 1.7, "Seeds contain polyunsaturated fatty acids that lower circulating serum cholesterol.", "Eastern Indian diabetic classic."),
    ("Ivy Gourd / Tindora (Kundru)", "Kundru", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 18, 1.2, 3.1, 1.6, 0.1, 120, 3, 40, 1.4, "Contains enzymes that regulate glucose-6-phosphatase, preventing liver glucose dumping.", "Evidence-based blood sugar modulator."),
    ("Lady's Finger / Okra (Bhindi)", "Bhindi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 20, 33, 1.9, 7.5, 3.2, 0.2, 299, 7, 82, 0.6, "Soluble mucilage binds cholesterol and delays glucose uptake in the intestine.", "Top dietary recommendation for diabetes."),
    ("Brinjal / Eggplant (Baingan / Purple)", "Baingan", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 25, 1.0, 5.9, 3.0, 0.2, 229, 2, 9, 0.2, "Nasunin, an anthocyanin in the purple skin, protects brain cell membranes from lipid peroxidation.", "Antioxidant rich vegetable."),
    ("Small Green Brinjal (Chota Baingan)", "Hara Baingan", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 24, 1.1, 5.5, 3.4, 0.2, 235, 3, 18, 0.3, "High fiber-to-calorie ratio; tender seeds provide healthy polyphenols.", "Stuffed baingan staple."),
    ("Cauliflower (Phool Gobhi)", "Phool Gobhi", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 25, 1.9, 5.0, 2.0, 0.3, 299, 30, 22, 0.4, "Glucosinolates and choline support hepatic detoxification and lipid metabolism.", "Low-carb keto/diabetic rice substitute."),
    ("Cabbage Green (Patta Gobhi)", "Patta Gobhi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 25, 1.3, 5.8, 2.5, 0.1, 170, 18, 40, 0.5, "High in vitamin C, vitamin K, and glutamine; protects stomach lining from ulcers.", "Everyday versatile vegetable."),
    ("Red Cabbage (Lal Gobhi)", "Lal Patta Gobhi", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 31, 1.4, 7.4, 2.1, 0.2, 243, 27, 45, 0.8, "10x higher anthocyanin content than green cabbage; potent protector of cardiac vessels.", "Cardiovascular antioxidant champion."),
    ("Broccoli Florets", "Hari Gobhi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 34, 2.8, 6.6, 2.6, 0.4, 316, 33, 47, 0.7, "Sulforaphane reduces hepatic gluconeogenesis and preserves pancreatic beta-cell health.", "Cruciferous metabolic protector."),
    ("Green Bell Pepper / Capsicum (Shimla Mirch)", "Hari Shimla Mirch", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 20, 0.9, 4.6, 1.7, 0.2, 175, 3, 10, 0.4, "Rich in capsiate and vitamin C (80mg); stimulates metabolism without burning heat.", "Low-sodium antioxidant crunch."),
    ("Red Bell Pepper (Lal Shimla Mirch)", "Lal Shimla Mirch", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 26, 1.0, 6.0, 2.1, 0.3, 211, 4, 7, 0.4, "Contains nearly 200% daily Vitamin C requirement; protects arterial collagen from breakdown.", "Vascular collagen builder."),
    ("Yellow Bell Pepper (Pili Shimla Mirch)", "Pili Shimla Mirch", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 27, 1.0, 6.3, 1.9, 0.2, 212, 3, 11, 0.5, "Lutein and violaxanthin safeguard retinal capillaries from high glucose toxicity.", "Eye and heart protector."),
    ("French Beans (Phasali)", "French Beans", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 15, 31, 1.8, 7.1, 2.7, 0.2, 211, 6, 37, 1.0, "Low glycemic impact and high silicon; strengthens connective tissue and bone matrix.", "Crisp diabetic staple vegetable."),
    ("Cluster Beans (Gawar Phali)", "Gawar Phali", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 15, 34, 3.2, 5.0, 5.4, 0.4, 270, 8, 130, 1.1, "Primary botanical source of guar gum; clinically proven to dramatically flatten glucose curves.", "Highest soluble fiber pod vegetable."),
    ("Broad Beans / Flat Beans (Sem Phali)", "Sem Phali", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 32, 2.5, 5.5, 4.0, 0.3, 240, 10, 80, 1.5, "High protein vegetable pods; promotes sustained fullness.", "Winter bean favorite."),
    ("Drumstick Pods (Sahjan / Moringakai)", "Sahjan Phali", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 26, 2.1, 3.7, 3.2, 0.2, 259, 9, 30, 0.4, "Bioactive isothiocyanates and oleic acid support lipid reduction and blood pressure regulation.", "Essential sambar and curry vegetable."),
    ("Cucumber English (Kheera)", "Kheera", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 15, 0.7, 3.6, 0.5, 0.1, 147, 2, 16, 0.3, "Cucurbitacins and 95% water content; flushes uric acid and helps control appetite.", "Hydrating zero-fat salad staple."),
    ("Indian Desi Cucumber (Kakdi)", "Kakdi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 13, 0.6, 2.8, 0.6, 0.1, 160, 2, 20, 0.4, "Crisp, cooling summer vegetable with high potassium and zero sodium load.", "Hydrating summer favorite."),
    ("Tomato Ripe Red (Tamatar)", "Tamatar", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 18, 0.9, 3.9, 1.2, 0.2, 237, 5, 10, 0.3, "Packed with lycopene, a carotenoid proven to reduce arterial stiffness and prevent LDL oxidation.", "Cardioprotective kitchen staple."),
    ("Raw Green Tomato (Hara Tamatar)", "Kaccha Tamatar", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 23, 1.2, 5.1, 1.4, 0.2, 204, 13, 13, 0.5, "Tomatidine stimulates muscle protein synthesis and inhibits fat accumulation.", "Tangy chutney and curry vegetable."),
    ("Pumpkin Yellow (Kaddu / Sitaphal)", "Kaddu / Kashiphal", veg_all, [], ["heart_healthy", "low_sodium"], 65, 26, 1.0, 6.5, 0.5, 0.1, 340, 1, 21, 0.8, "High beta-carotene and lutein; low calorie density despite rich sweet flavor.", "Ayurvedic soothing vegetable."),
    ("Green Pumpkin (Hara Kaddu)", "Hara Kaddu", veg_all, [], ["diabetic_friendly", "low_gi"], 55, 22, 1.2, 4.8, 1.1, 0.1, 290, 2, 18, 0.6, "Mild sweet taste with lower sugar and higher fiber than yellow pumpkin.", "Everyday sabzi choice."),
    ("Raw Banana (Kaccha Kela)", "Kaccha Kela", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 45, 89, 1.1, 22.8, 2.6, 0.3, 358, 1, 5, 0.3, "Loaded with resistant starch (Type 2); bypasses small intestine to nourish colon cells with butyrate.", "Prebiotic diabetic gut staple."),
    ("Banana Flower / Plantain Blossom (Kele ka Phool)", "Kele ka Phool", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 15, 51, 1.6, 9.9, 5.7, 0.6, 553, 19, 32, 5.6, "Reduces bleeding disorders, lowers fasting blood glucose, and supports progesterone balance.", "Therapeutic South Indian blossom."),
    ("Banana Stem (Vazhaithandu / Kele ka Doodh)", "Kele ka Tana", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium", "high_fiber"], 15, 14, 0.5, 3.0, 4.0, 0.1, 320, 5, 25, 1.2, "Rich in potassium and high fiber; renowned in traditional medicine for flushing kidney stones.", "Renal and blood pressure cleanser."),
    ("Zucchini Green", "Zucchini", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 17, 1.2, 3.1, 1.0, 0.3, 261, 8, 16, 0.4, "Ultra-low calorie squash; easy to spiralize into low-carb noodles (zoodles).", "Diabetic pasta alternative."),
    ("Yellow Zucchini", "Pili Zucchini", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 16, 1.2, 3.0, 1.0, 0.2, 255, 7, 15, 0.4, "Crisp tender squash rich in zeaxanthin for visual retina protection.", "Low-carb colorful vegetable."),
    ("Knol Khol / Kohlrabi (Ganth Gobhi)", "Ganth Gobhi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 15, 27, 1.7, 6.2, 3.6, 0.1, 350, 20, 24, 0.4, "Cruciferous swollen stem packed with vitamin C (62mg) and potassium.", "Crisp Kashmiri favorite."),
    ("Raw Mango (Kaccha Aam / Kairi)", "Kairi", veg_all, [], ["hypertension_friendly", "low_sodium"], 35, 60, 0.8, 15.0, 1.6, 0.4, 168, 2, 14, 0.2, "Pectin and citric acid prevent sunstroke and replenish intracellular electrolytes.", "Cooling summer beverage and pickle base."),
    ("Raw Jackfruit (Kaccha Kathal)", "Kathal", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 40, 95, 1.7, 23.2, 4.0, 0.6, 448, 2, 24, 0.5, "Clinically proven to reduce HbA1c when replacing rice/wheat flour due to high insoluble fiber.", "The vegetarian super-meat for diabetics."),
    ("Lotus Stem (Kamal Kakdi / Nadru)", "Kamal Kakdi / Nadru", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"], 15, 74, 2.6, 17.2, 4.9, 0.1, 556, 40, 45, 1.2, "Complex dietary fiber binds bile acids; high potassium relaxes arterial pressure.", "Crisp Kashmiri aquatic delicacy."),
    ("Water Chestnuts Fresh (Singhara)", "Singhara Taaza", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 45, 97, 1.4, 23.9, 3.0, 0.1, 584, 14, 11, 0.8, "Crunchy aquatic tuber with high potassium; counters excess dietary sodium.", "Crisp seasonal autumn snack."),
    ("Colocasia Stem (Arbi ka Danda)", "Arbi Dandi", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 15, 0.6, 3.2, 2.5, 0.1, 180, 5, 60, 0.8, "Fibrous stalks cooked in coastal curries; gentle on blood sugar.", "Traditional coastal stalk."),
    ("Tender Bamboo Shoots (Baans ke Karil)", "Baans Karil", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 15, 27, 2.6, 5.2, 2.2, 0.3, 533, 4, 13, 0.5, "Phytosterols lower blood lipid levels; high fiber promotes regular bowel movements.", "Northeastern delicacy."),
    ("Tinda / Apple Gourd", "Tinda", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 21, 1.4, 3.4, 1.6, 0.2, 175, 2, 25, 0.9, "94% water content; soothes the digestive tract and cools the urinary system.", "Light North Indian summer sabzi."),
    ("Chayote / Chow-Chow (Bangalore Brinjal)", "Chow-Chow", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 19, 0.8, 4.5, 1.7, 0.1, 125, 2, 17, 0.3, "High folate and myricetin; supports lipid breakdown and reduces systemic inflammation.", "Versatile South Indian kootu vegetable."),
    ("Parwal / Wax Gourd Tender", "Kaccha Parwal", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 19, 1.8, 2.5, 2.8, 0.2, 210, 3, 28, 1.5, "Light on the stomach; proven in research to enhance glucose uptake in peripheral tissues.", "Healthy convalescent sabzi."),
    ("Baby Corn Fresh", "Baby Corn", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 26, 2.6, 3.0, 3.0, 0.4, 280, 5, 28, 0.8, "Harvested before starch accumulation; behaves like a non-starchy leafy vegetable.", "Crisp low-carb stir-fry veggie."),
    ("Mushroom White Button (Khumb)", "Khumb", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"], 15, 22, 3.1, 3.3, 1.0, 0.3, 318, 5, 3, 0.5, "Rich in ergothioneine and beta-glucan; enhances immune cell activity without raising blood sugar.", "Low-calorie protein powerhouse."),
    ("Mushroom Cremini / Brown", "Brown Mushroom", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 22, 2.5, 3.7, 1.2, 0.1, 448, 6, 18, 0.6, "High selenium and copper; guards against vascular oxidative stress.", "Antioxidant rich fungal food."),
    ("Mushroom Portobello", "Portobello", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 22, 2.1, 3.9, 1.3, 0.4, 364, 9, 3, 0.5, "Meaty texture; excellent low-sodium plant patty substitute for burgers.", "Meat alternative for cardiac health."),
    ("Mushroom Oyster (Dhingri)", "Dhingri", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein"], 15, 33, 3.3, 6.1, 2.3, 0.4, 420, 18, 3, 1.3, "Naturally contains lovastatin, an HMG-CoA reductase inhibitor that naturally lowers LDL.", "Cardioprotective cultivated mushroom."),
    ("Mushroom Shiitake Fresh", "Shiitake", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 34, 2.2, 6.8, 2.5, 0.5, 304, 9, 2, 0.4, "Lentinan polysaccharides stimulate macrophages and defend vascular walls.", "Therapeutic immune mushroom."),
    ("Green Papaya Raw (Kaccha Papita)", "Kaccha Papita", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 32, 0.7, 7.2, 1.8, 0.2, 257, 3, 16, 0.3, "Abundant papain and chymopapain enzymes; accelerates gastrointestinal protein breakdown.", "Natural digestive enzyme sabzi."),
    ("Spine Gourd / Teasle Gourd (Kantola / Kakrol)", "Kantola", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 28, 3.1, 3.2, 3.0, 0.6, 290, 4, 33, 1.4, "Seasonal monsoon vegetable with high flavonoids and potent insulin-mimetic activity.", "Wild antidiabetic delicacy."),
    ("Elephant Apple (Chalta)", "Chalta", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 59, 0.8, 13.0, 2.5, 0.2, 180, 5, 16, 0.6, "Betulinic acid in the fruit pulp exhibits protective antihyperglycemic action.", "Eastern Indian traditional fruit-vegetable."),
    ("Caper Berries (Kair)", "Kair", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 35, 2.0, 6.0, 3.5, 0.5, 310, 8, 45, 1.2, "Arid desert vegetable rich in glucocapparin; used in Rajasthan to relieve metabolic sluggishness.", "Pungent Rajasthani super-berry."),
    ("Cluster Bean Pods Tender", "Chhoti Gawar Phali", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 32, 3.0, 4.8, 5.0, 0.3, 260, 7, 125, 1.0, "Tender young gawar pods; highest soluble galactomannan fiber.", "Superior blood sugar controller."),
    ("String Beans / Yardlong Beans (Borbati / Lobia Phali)", "Borbati", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 47, 2.8, 8.3, 3.6, 0.4, 240, 4, 50, 1.0, "Long tender pods rich in Vitamin A and soluble fiber.", "Staple green bean."),
    ("Amaranth Tender Stem", "Chaulai Danda", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 18, 1.1, 3.0, 2.5, 0.2, 220, 8, 85, 1.2, "Succulent stems rich in minerals and water; cooked in sambar.", "Mineral-rich succulent stem."),
    ("Lotus Seed Fresh (Kachha Makhana)", "Kachha Makhana", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 45, 89, 4.1, 17.0, 2.0, 0.5, 350, 3, 40, 1.1, "Fresh green lotus seeds eaten raw; soothing to heart palpitations.", "Ayurvedic cardiac cooling seed."),
    ("Colocasia Corm Tender", "Arbi Ganth", veg_all, [], ["high_fiber"], 54, 112, 1.5, 26.5, 4.1, 0.2, 591, 11, 43, 0.5, "High potassium (591mg) and resistant starch; baked or boiled for steady energy.", "Starchy root vegetable."),
    ("Drumstick Flowers (Sahjan ke Phool)", "Sahjan Phool", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 15, 31, 2.5, 4.5, 2.8, 0.5, 280, 6, 90, 1.8, "Delicate flowers with antimicrobial pterygospermin; supports liver health.", "Therapeutic seasonal flower."),
    ("Pumpkin Flowers (Kaddu ke Phool)", "Kaddu Phool", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 15, 1.0, 3.3, 1.5, 0.1, 134, 5, 39, 0.7, "High in vitamin A and lutein; dipped in besan for healthy baked fritters.", "Delicate edible flower."),
    ("Sesbania Flowers (Bokphool)", "Bokphool", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 27, 1.5, 5.0, 1.8, 0.2, 180, 8, 42, 0.8, "White flowers used in Bengal; cleanses respiratory and digestive tract.", "Traditional medicinal bloom."),
    ("Banana Blossom Inner Floret", "Kela Phool Dodi", veg_all, [], ["diabetic_friendly", "low_gi", "high_fiber"], 15, 48, 1.8, 9.0, 5.2, 0.4, 520, 15, 30, 4.8, "Tender interior florets rich in magnesium; reduces anxiety and blood sugar.", "Ayurvedic uterine and metabolic tonic."),
    ("Chive Leaves & Shoots", "Chives", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 30, 3.3, 4.4, 2.5, 0.7, 296, 3, 92, 1.6, "Allicin content relaxes blood vessels and inhibits platelet aggregation.", "Onion-scented delicate herb."),
    ("Leeks Green & White", "Leek", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 61, 1.5, 14.2, 1.8, 0.3, 180, 20, 59, 2.1, "Kaempferol bioflavonoid protects blood vessel linings from damage.", "Alliin-rich soup vegetable."),
    ("Scallions / Spring Onion Green", "Hari Pyaz", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 32, 1.8, 7.3, 2.6, 0.2, 276, 16, 72, 1.5, "Sulfur phytochemicals inhibit cholesterol synthesis in hepatic cells.", "Fresh allium crunch."),
    ("Shallots / Small Sambhar Onion", "Chota Pyaz", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 15, 72, 2.5, 16.8, 3.2, 0.1, 334, 12, 37, 1.2, "Rich in quercetin and allicin; 6x higher polyphenol concentration than large white onions.", "Cardiovascular South Indian staple."),
    ("Red Onion Bulb (Pyaz)", "Lal Pyaz", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 40, 1.1, 9.3, 1.7, 0.1, 146, 4, 23, 0.2, "Quercetin bioflavonoid lowers systolic blood pressure and fights systemic inflammation.", "Universal Indian kitchen foundation."),
    ("White Onion Bulb (Safed Pyaz)", "Safed Pyaz", veg_all, [], ["diabetic_friendly", "low_gi"], 15, 42, 1.2, 9.8, 1.5, 0.1, 150, 3, 25, 0.3, "Prized in Ayurveda for cooling the body in heatwaves and soothing the stomach.", "Cooling summer allium."),
    ("Garlic Cloves Raw (Lahsun)", "Lahsun", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "low_sodium"], 15, 149, 6.4, 33.1, 2.1, 0.5, 401, 17, 181, 1.7, "Allicin stimulates endothelial nitric oxide production; reduces both systolic and diastolic BP.", "Clinical herbal ACE inhibitor food."),
    ("Ginger Root Fresh (Adrak)", "Adrak", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 80, 1.8, 17.8, 2.0, 0.8, 415, 13, 16, 0.6, "Gingerols accelerate gastric emptying, reduce nausea, and improve insulin receptor sensitivity.", "Universal digestive medicine."),
    ("Turmeric Root Fresh (Kacchi Haldi)", "Kacchi Haldi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 67, 1.6, 14.5, 2.5, 0.5, 380, 10, 30, 2.5, "Curcumin is a premier anti-inflammatory; downregulates NF-kB and shields vascular endothelium.", "The golden healer root.")
]
for v in other_veg:
    add(v[0], v[1], "Other Vegetables", v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12], v[13], v[14], v[15], v[16])

print(f"Items after Other Veg: {len(all_foods)}")

# Save to check progress
print("Done step 1.")
