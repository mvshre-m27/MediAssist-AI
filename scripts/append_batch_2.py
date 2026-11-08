"""
Batch 2 Appender: Fruits, Nuts, Spices, Dairy, Animal Foods, Beverages, and Healthy Oils.
Brings total IFCT foods to 560+ items.
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
# 6. FRUITS (72 items)
# =========================================================================
fruits = [
    ("Indian Gooseberry (Amla)", "Amla", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 48, 0.5, 13.7, 3.4, 0.1, 225, 2, 50, 1.2, "World's most concentrated natural Vitamin C source (600mg/100g); tannins protect ascorbic acid from heat degradation, improving endothelial function.", "Premier Ayurvedic Rasayana fruit."),
    ("Guava White Flesh (Amrood)", "Safed Amrood", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"], 30, 68, 2.6, 14.3, 5.4, 1.0, 417, 2, 18, 0.3, "High soluble pectin fiber slows glucose absorption; high potassium relaxes arterial pressure.", "Top clinical diabetic fruit."),
    ("Guava Pink Flesh (Lal Amrood)", "Gulabi Amrood", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"], 30, 68, 2.6, 14.0, 5.2, 1.0, 420, 2, 20, 0.4, "Contains double the lycopene of tomatoes; guards cardiovascular system against plaque.", "Lycopene-rich pink guava."),
    ("Pomegranate (Anar)", "Anar", veg_all, [], ["hypertension_friendly", "heart_healthy", "low_sodium"], 53, 83, 1.7, 18.7, 4.0, 1.2, 236, 3, 10, 0.3, "Punicalagins exert natural ACE-inhibitory action, reducing systolic BP by up to 5-10 mmHg.", "Cardioprotective jewel fruit."),
    ("Papaya Ripe (Paka Papita)", "Paka Papita", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 60, 43, 0.5, 10.8, 1.7, 0.3, 182, 8, 20, 0.1, "Lycopene and papain enzyme soothe GI tract; low glycemic load (GL: 4.8) per standard serving.", "Moderate GI, low glycemic load fruit."),
    ("Jamun / Black Plum (Java Plum)", "Jamun", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 25, 60, 0.7, 15.6, 0.9, 0.2, 79, 14, 19, 0.2, "Jamboline glucoside prevents the conversion of starch into glucose; anthocyanins protect beta cells.", "Legendary Indian antidiabetic fruit."),
    ("Apple Green (Granny Smith)", "Hara Seb", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 36, 52, 0.3, 13.8, 2.4, 0.2, 107, 1, 6, 0.1, "Quercetin flavonoid improves insulin sensitivity; pectin fiber cleanses LDL cholesterol.", "Low sugar crisp apple."),
    ("Apple Red Delicious (Seb)", "Lal Seb", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 38, 52, 0.3, 14.0, 2.4, 0.2, 110, 1, 6, 0.1, "Pectin forms a gel barrier in intestine slowing sugar absorption; peel contains triterpenoids.", "Heart healthy classic fruit."),
    ("Wild Blueberries (Indian Cultivated)", "Blueberry", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 40, 57, 0.7, 14.5, 2.4, 0.3, 77, 1, 6, 0.3, "Anthocyanins increase GLUT4 translocation in skeletal muscle, dramatically lowering insulin resistance.", "Neurological & metabolic berry."),
    ("Blackberries", "Blackberry", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 25, 43, 1.4, 9.6, 5.3, 0.5, 162, 1, 29, 0.6, "Very low net carbs and very high fiber; cyanidin-3-glucoside inhibits carbohydrate digestive enzymes.", "Ultra low GI berry."),
    ("Strawberries", "Strawberry", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 41, 33, 0.7, 7.7, 2.0, 0.3, 153, 1, 16, 0.4, "Fisetin and ellagic acid suppress post-meal glycemic surges and protect renal microvessels.", "Low-sugar anti-inflammatory fruit."),
    ("Raspberries", "Raspberry", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 32, 52, 1.2, 11.9, 6.5, 0.7, 151, 1, 25, 0.7, "Rhubarb-like rheosmin stimulates fat cell metabolism; highest fiber percentage among berries.", "High fiber metabolic berry."),
    ("Cranberries (Fresh / Unsweetened)", "Cranberry", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 35, 46, 0.4, 12.2, 4.6, 0.1, 85, 2, 8, 0.3, "Proanthocyanidins prevent bacterial adhesion in urinary tract; natural diuretic.", "Renal and bladder protective berry."),
    ("Indian Mulberry (Shahtoot)", "Shahtoot", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 25, 43, 1.4, 9.8, 1.7, 0.4, 194, 10, 39, 1.9, "1-deoxynojirimycin (DNJ) competitively inhibits intestinal alpha-glucosidase.", "Ancient blood sugar balancer."),
    ("Cape Gooseberry / Rasbhari (Physalis)", "Rasbhari", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 30, 53, 1.9, 11.2, 4.9, 0.7, 280, 2, 9, 1.0, "Withanolides and pectin support liver function and lower inflammatory markers.", "Tangy antioxidant berry."),
    ("Phalsa (Grewia Asiatica)", "Phalsa", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 25, 72, 1.3, 14.7, 1.2, 0.1, 350, 4, 129, 3.1, "Rich in anthocyanins, potassium, and calcium; renowned cooling summer tonic.", "Ayurvedic cardiac refrigerant."),
    ("Indian Jujube / Ber (Ziziphus)", "Ber", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 35, 79, 1.2, 20.2, 3.0, 0.2, 250, 3, 26, 0.5, "High vitamin C and betulinic acid; soothes anxiety, insomnia, and palpitations.", "Traditional seasonal fruit."),
    ("Sweet Lime (Mosambi)", "Mosambi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 40, 43, 0.8, 9.3, 1.2, 0.3, 490, 2, 40, 0.7, "Potassium (490mg) relaxes peripheral resistance; hesperidin bioflavonoid enhances capillary strength.", "Cardiovascular citrus fruit."),
    ("Orange (Santra / Nagpur Orange)", "Santra", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 43, 47, 0.9, 11.8, 2.4, 0.1, 181, 0, 40, 0.1, "Naringenin and vitamin C prevent lipid peroxidation and endothelial dysfunction.", "Classic vitamin C citrus."),
    ("Kinnow", "Kinnow", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 42, 48, 0.9, 12.0, 2.2, 0.1, 190, 1, 42, 0.2, "Juicy hybrid mandarin with high limonene; stimulates phase II detox enzymes.", "Refreshing citrus."),
    ("Grapefruit Pink (Chakotra)", "Chakotra", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 25, 42, 0.8, 10.7, 1.6, 0.1, 135, 0, 22, 0.1, "Naringin improves insulin sensitivity. NOTE: Interacts with statins and amlodipine.", "Potent insulin-sensitizing citrus."),
    ("Pomelo (Batabi Lebu / Big Citrus)", "Batabi Lebu", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 30, 38, 0.8, 9.6, 1.0, 0.0, 216, 1, 4, 0.1, "Giant citrus packed with potassium; low sodium and high bioflavonoids.", "Refreshing monsoon citrus."),
    ("Lemon Fresh (Nimbu)", "Kagzi Nimbu", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium"], 15, 29, 1.1, 9.3, 2.8, 0.3, 138, 2, 26, 0.6, "Citric acid and hesperidin prevent kidney stone crystallization and support vascular integrity.", "Daily detoxifier."),
    ("Lime (Kachha Nimbu)", "Chota Nimbu", veg_all, [], ["diabetic_friendly", "low_gi", "low_sodium"], 15, 30, 0.7, 10.5, 2.8, 0.2, 102, 2, 33, 0.6, "Alkalinizes urine despite acidic taste; reduces systemic uric acid load.", "Alkaline systemic toner."),
    ("Raw Mango (Kaccha Aam)", "Kaccha Aam", veg_all, [], ["hypertension_friendly", "low_sodium"], 35, 60, 0.8, 15.0, 1.6, 0.4, 168, 2, 14, 0.2, "Abundant pectin and malic acid prevent dehydration and electrolyte loss in heat.", "Aam panna electrolyte fruit."),
    ("Ripe Mango (Alphonso / Hapus)", "Hapus Aam", veg_all, [], ["heart_healthy"], 60, 65, 0.8, 17.0, 1.6, 0.4, 168, 1, 11, 0.2, "Rich in mangiferin, a polyphenol that exhibits strong cardioprotective and antioxidant activity.", "King of Indian fruits."),
    ("Ripe Mango (Dasheri)", "Dasheri Aam", veg_all, [], [], 60, 62, 0.7, 16.5, 1.5, 0.3, 160, 1, 10, 0.2, "Sweet aromatic flesh rich in beta-carotene; consume in controlled portions for diabetics.", "Aromatic summer mango."),
    ("Ripe Mango (Kesar)", "Kesar Aam", veg_all, [], [], 60, 64, 0.8, 16.8, 1.6, 0.3, 165, 1, 12, 0.2, "Saffron-scented Gujarati mango packed with vitamin A and prebiotic oligosaccharides.", "Gujarat's queen mango."),
    ("Ripe Mango (Langra)", "Langra Aam", veg_all, [], [], 58, 63, 0.8, 16.2, 1.8, 0.3, 170, 1, 12, 0.3, "Fibrous green-skin mango with lower glycemic response than very sweet cultivars.", "Tangy sweet summer mango."),
    ("Watermelon (Tarbooj)", "Tarbooj", veg_all, [], ["hypertension_friendly", "heart_healthy", "low_sodium"], 72, 30, 0.6, 7.6, 0.4, 0.2, 112, 1, 7, 0.2, "L-citrulline amino acid converts to L-arginine, directly boosting nitric oxide synthesis to lower arterial BP.", "Vasodilating hydration fruit."),
    ("Muskmelon (Kharbuja)", "Kharbuja", veg_all, [], ["hypertension_friendly", "low_sodium"], 65, 34, 0.8, 8.2, 0.9, 0.2, 267, 16, 9, 0.2, "Adenosine compound prevents blood clotting; high potassium and water content.", "Heart-soothing summer melon."),
    ("Honeydew Melon (Sharbatkhar)", "Honeydew", veg_all, [], ["hypertension_friendly", "low_sodium"], 62, 36, 0.5, 9.1, 0.8, 0.1, 228, 18, 6, 0.2, "Subtle sweet melon packed with potassium and folate; supports blood pressure balance.", "Cooling pale melon."),
    ("Pineapple Fresh (Ananas)", "Ananas", veg_all, [], ["heart_healthy"], 59, 50, 0.5, 13.1, 1.4, 0.1, 109, 1, 13, 0.3, "Bromelain proteolytic enzyme dissolves fibrin blood clots and reduces inflammatory edema.", "Digestive and anti-edema fruit."),
    ("Ripe Banana (Kela / Robusta)", "Robusta Kela", veg_all, [], ["hypertension_friendly", "heart_healthy"], 51, 89, 1.1, 22.8, 2.6, 0.3, 358, 1, 5, 0.3, "High potassium (358mg) and Vitamin B6; essential for regulating cellular sodium-potassium ATPase pump.", "DASH diet staple fruit."),
    ("Small Banana (Yellaki / Elaichi Kela)", "Elaichi Kela", veg_all, [], ["hypertension_friendly"], 48, 92, 1.2, 23.5, 2.8, 0.3, 380, 1, 6, 0.3, "Firm texture, dense potassium, and lower water content; excellent pre-workout fuel.", "Traditional temple banana."),
    ("Red Banana (Lal Kela / Sevvazhai)", "Lal Kela", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 45, 90, 1.3, 23.0, 3.0, 0.3, 400, 1, 10, 0.4, "High carotenoid and anthocyanin content; lower glycemic index than regular yellow cavendish.", "Antioxidant South Indian banana."),
    ("Nendran Banana (Kerala Plantain)", "Nendran Kela", veg_all, [], ["hypertension_friendly"], 52, 95, 1.4, 24.0, 2.8, 0.3, 370, 1, 8, 0.4, "Starchy firm banana; steamed for healthy breakfast in Kerala ayurvedic tradition.", "Traditional Kerala energy fruit."),
    ("Sapota / Chiku (Sapodilla)", "Chiku", veg_all, [], ["high_fiber"], 65, 83, 0.4, 20.0, 5.3, 1.1, 193, 12, 21, 0.8, "Extremely high dietary fiber (5.3g/100g); promotes intestinal peristalsis.", "Energy and fiber rich fruit."),
    ("Custard Apple / Sitaphal (Sharifa)", "Sitaphal", veg_all, [], ["hypertension_friendly"], 54, 94, 2.1, 23.6, 4.4, 0.3, 247, 9, 24, 0.6, "Rich in magnesium (21% DV) which relaxes heart muscle; sweet creamy texture.", "Cardiac magnesium rich fruit."),
    ("Pappadam / Ramphal (Bullock's Heart)", "Ramphal", veg_all, [], ["hypertension_friendly"], 52, 75, 1.7, 18.0, 3.5, 0.3, 260, 8, 22, 0.5, "Lesser-known cousin of sitaphal; contains annonacin that helps combat hyperlipidemia.", "Indigenous heart-shaped fruit."),
    ("Sour Sop (Laxmanphal / Graviola)", "Laxmanphal", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 35, 66, 1.0, 16.8, 3.3, 0.3, 278, 14, 14, 0.6, "Acetogenins show potent cytotoxic effects against abnormal cells and support metabolic balance.", "Traditional therapeutic fruit."),
    ("Fresh Fig (Anjeer Taaza)", "Anjeer Taaza", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"], 35, 74, 0.8, 19.2, 2.9, 0.3, 232, 1, 35, 0.4, "Ficusin and chlorogenic acid improve glucose metabolism; mucilaginous fiber cleanses bowels.", "Ancient therapeutic fruit."),
    ("Dried Fig (Sukha Anjeer)", "Sukha Anjeer", veg_all, [], ["hypertension_friendly", "high_fiber", "high_calcium", "high_iron"], 55, 249, 3.3, 63.9, 9.8, 0.9, 680, 10, 162, 2.0, "High calcium (162mg) and potassium (680mg); soak overnight to soften for cardiac and bone health.", "Dense mineral dried fruit."),
    ("Fresh Dates (Khajoor)", "Taza Khajoor", veg_all, [], ["heart_healthy", "high_fiber"], 50, 142, 1.8, 37.0, 3.5, 0.4, 320, 2, 35, 1.0, "High polyphenols with lower sugar concentration than dehydrated dates.", "Antioxidant fresh date."),
    ("Dried Dates (Chhuhara)", "Chhuhara", veg_all, [], ["high_fiber", "high_calcium", "high_iron"], 62, 282, 2.5, 75.0, 8.0, 0.4, 650, 2, 64, 4.8, "Traditional convalescent tonic boiled in milk; exceptional bioavailable iron.", "Iron and bone tonic."),
    ("Medjool Dates", "Medjool Khajoor", veg_all, [], ["high_fiber"], 55, 277, 1.8, 75.0, 6.7, 0.2, 696, 1, 64, 0.9, "Plump caramel dates with high potassium; clean natural sweetener for diabetic snacks.", "Gourmet natural sweetener."),
    ("Black Grapes (Kala Angoor)", "Kala Angoor", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 45, 69, 0.7, 18.1, 0.9, 0.2, 191, 2, 10, 0.4, "Resveratrol in the black skin enhances endothelial nitric oxide and inhibits platelet clotting.", "Cardioprotective resveratrol grape."),
    ("Green Seedless Grapes (Hara Angoor)", "Hara Angoor", veg_all, [], ["heart_healthy"], 53, 69, 0.7, 18.1, 0.9, 0.2, 191, 2, 10, 0.4, "Quercetin and catechins provide cardiovascular protection; enjoy in moderation.", "Classic table grape."),
    ("Red Globe Grapes", "Lal Angoor", veg_all, [], ["heart_healthy"], 49, 67, 0.6, 17.5, 1.0, 0.2, 190, 2, 12, 0.4, "Contains proanthocyanidins in seeds and skins; strengthens capillary permeability.", "Crisp seeded grape."),
    ("Raisins / Kishmish (Golden)", "Kishmish", veg_all, [], ["high_fiber", "high_iron"], 64, 299, 3.1, 79.2, 3.7, 0.5, 749, 11, 50, 1.9, "High potassium (749mg), boron, and tartaric acid; supports bone and colon health.", "Natural sweet raisin."),
    ("Black Raisins with Seeds (Munakka)", "Munakka", veg_all, [], ["hypertension_friendly", "heart_healthy", "high_iron"], 58, 290, 3.3, 76.0, 4.5, 0.4, 820, 10, 80, 3.2, "Ayurvedic Rasayana soaked overnight in water; soothes cardiac fatigue and purifies blood.", "Therapeutic medicinal raisin."),
    ("Pear Indian (Nashpati)", "Nashpati", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 38, 57, 0.4, 15.2, 3.1, 0.1, 116, 1, 9, 0.2, "Pectin and epicatechin promote heart health; high water-to-sugar ratio.", "Crisp everyday pear."),
    ("Chinese Pear (Babgona)", "Babgona", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 36, 42, 0.5, 10.6, 3.6, 0.1, 121, 0, 8, 0.2, "Extremely crisp and juicy with very low calorie density; safe diabetic snacking.", "Juicy low-carb pear."),
    ("Plum (Aloo Bukhara)", "Aloo Bukhara", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 40, 46, 0.7, 11.4, 1.4, 0.3, 157, 0, 6, 0.2, "Chlorogenic acid helps regulate blood glucose; sorbitol gently relieves constipation.", "Antioxidant stone fruit."),
    ("Dried Plum (Prune)", "Sukha Aloo Bukhara", veg_all, [], ["high_fiber"], 52, 240, 2.2, 63.9, 7.1, 0.4, 732, 2, 43, 0.9, "World's most studied fruit for reversing osteoporosis due to boron and vitamin K.", "Bone and bowel super-fruit."),
    ("Peach (Aadoo)", "Aadoo", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 42, 39, 0.9, 9.5, 1.5, 0.3, 190, 0, 6, 0.3, "Caffeic acid in skin fights metabolic syndrome and obesity-related diabetes.", "Delicate stone fruit."),
    ("Apricot Fresh (Khubani)", "Khubani Taaza", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 34, 48, 1.4, 11.1, 2.0, 0.4, 259, 1, 13, 0.4, "High lutein, zeaxanthin, and potassium; protects vascular and macular capillaries.", "Low-GI stone fruit."),
    ("Apricot Dried (Jardalu)", "Sukhi Khubani", veg_all, [], ["hypertension_friendly", "high_fiber", "high_iron"], 55, 241, 3.4, 62.6, 7.3, 0.5, 1162, 10, 55, 2.7, "Extremely high potassium (1162mg); counteracts hypertension and sodium retention.", "Potassium-dense dried fruit."),
    ("Cherries Fresh (Kashmiri Cherries)", "Kashmiri Cherry", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 22, 50, 1.0, 12.0, 1.6, 0.3, 173, 0, 16, 0.3, "Lowest GI fruit (22); anthocyanins lower elevated serum uric acid and reduce gout attacks.", "Gout and diabetic champion fruit."),
    ("Kiwi Fruit (Indian Green)", "Kiwi", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 48, 61, 1.1, 14.7, 3.0, 0.5, 312, 3, 34, 0.3, "Actinidain enzyme digests dietary protein; eating 2 kiwis daily is proven to lower systolic BP by 10 mmHg.", "Clinically proven blood pressure fruit."),
    ("Wood Apple / Bael (Bilva Fruit)", "Bael Phal", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 35, 137, 1.8, 31.8, 2.9, 0.4, 600, 10, 85, 0.6, "Marmelosin compound heals gastrointestinal ulcers, controls diarrhea, and purifies blood.", "Sacred digestive healer fruit."),
    ("Star Fruit (Kamrakh / Carambola)", "Kamrakh", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly"], 35, 31, 1.0, 6.7, 2.8, 0.3, 133, 2, 3, 0.1, "Crunchy star slices rich in epicatechin and vitamin C. NOTE: Avoid in chronic kidney disease.", "Crisp low calorie fruit."),
    ("Dragon Fruit White Flesh (Kamalam)", "Kamalam", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 40, 60, 1.2, 13.0, 2.9, 0.5, 350, 4, 18, 0.7, "Tiny black seeds provide omega-3 and omega-9; lowers insulin resistance.", "Low-carb exotic cactus fruit."),
    ("Dragon Fruit Red Flesh (Lal Kamalam)", "Lal Kamalam", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 38, 62, 1.3, 13.5, 3.0, 0.6, 360, 4, 20, 0.8, "Betacyanins in red flesh provide intense antioxidant defense against lipid peroxidation.", "Antioxidant rich red fruit."),
    ("Passion Fruit (Indian Purple)", "Krishna Phal", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"], 30, 97, 2.2, 23.4, 10.4, 0.7, 348, 28, 12, 1.6, "Huge dietary fiber (10.4g/100g) and piceatannol; significantly improves insulin sensitivity.", "High fiber exotic fruit."),
    ("Avocado / Butter Fruit (Indian Grown)", "Butter Fruit / Makhanphal", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 15, 160, 2.0, 8.5, 6.7, 14.7, 485, 7, 12, 0.6, "Rich in monounsaturated oleic acid and potassium (485mg); enhances absorption of fat-soluble vitamins.", "Healthy fat super-fruit."),
    ("Litchi (Shahi Litchi / Muzaffarpur)", "Shahi Litchi", veg_all, [], [], 50, 66, 0.8, 16.5, 1.3, 0.4, 171, 1, 5, 0.3, "Oligonol polyphenol improves vascular flow and reduces post-exercise exhaustion.", "Sweet fragrant Bihar fruit."),
    ("Longan (Dimocarpus)", "Ashphal", veg_all, [], [], 52, 60, 1.3, 15.1, 1.1, 0.1, 266, 0, 1, 0.1, "Dragon-eye fruit with high gallic acid; traditional nervous relaxant.", "Delicate sweet fruit."),
    ("Persimmon (Japani Phal / Kaki)", "Japani Phal", veg_all, [], ["heart_healthy", "high_fiber"], 50, 70, 0.6, 18.6, 3.6, 0.2, 161, 1, 8, 0.2, "Rich in proanthocyanidins and soluble tannins that lower cholesterol and blood pressure.", "Autumn Himalayan fruit."),
    ("Quince (Bihi)", "Bihi", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"], 35, 57, 0.4, 15.3, 1.9, 0.1, 197, 4, 11, 0.7, "High pectin content calms stomach acid and coats esophageal membranes.", "Aromatic astringent fruit."),
    ("Tamarind Ripe Pulp (Imli)", "Imli", veg_all, [], ["diabetic_friendly", "low_gi", "heart_healthy"], 40, 239, 2.8, 62.5, 5.1, 0.6, 628, 28, 74, 2.8, "Tartaric acid and potassium (628mg); protects liver from alcohol and lipid toxicity.", "Traditional culinary acid."),
    ("Kokum Fresh / Dried Fruit (Vrikshamla)", "Kokum", veg_all, [], ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"], 25, 60, 1.0, 14.0, 3.5, 0.2, 380, 5, 45, 1.5, "Hydroxicitric acid (HCA) inhibits ATP-citrate lyase, suppressing fat synthesis and appetite.", "Konkan cardioprotective fruit.")
]
for f in fruits:
    add(f[0], f[1], "Fruits", f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], f[13], f[14], f[15], f[16])

print(f"Items after Fruits: {len(foods)}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
    json.dump(foods, f_out, indent=2)

print("Batch 2 step 1 complete.")
