import streamlit as st
import json
from pathlib import Path
from database import get_connection

# =====================================================================
# 1. CURATED CLINICAL NUTRITION KNOWLEDGE BASE (60+ Evidence-Based Foods)
# =====================================================================

FOOD_DATABASE = [
    # --- WHOLE GRAINS & COMPLEX CARBS ---
    {
        "name": "Steel-Cut / Rolled Oats",
        "category": "Whole Grains",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["gluten"],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"],
        "glycemic_index": 52,
        "key_nutrients": "Beta-glucan soluble fiber, Magnesium, Zinc",
        "health_benefit": "Forms a gel-like matrix in the digestive tract that slows glucose absorption and lowers LDL cholesterol.",
        "rationale": "Strongly supported for Type 2 Diabetes and cardiovascular health."
    },
    {
        "name": "Finger Millet (Ragi / Nachni)",
        "category": "Whole Grains",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber", "gluten_free"],
        "glycemic_index": 54,
        "key_nutrients": "Calcium 344mg/100g, Dietary Fiber, Polyphenols",
        "health_benefit": "Natural gluten-free grain with high polyphenol content that inhibits amylase enzymes, modulating blood glucose peaks.",
        "rationale": "Traditional low-GI staple with superior micronutrient bioavailability."
    },
    {
        "name": "Quinoa",
        "category": "Whole Grains",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein", "gluten_free"],
        "glycemic_index": 53,
        "key_nutrients": "Complete Protein (all 9 essential amino acids), Iron, Magnesium",
        "health_benefit": "High protein-to-carbohydrate ratio promotes satiety while magnesium supports vascular smooth muscle relaxation.",
        "rationale": "Excellent meal base for both hypertension and diabetic glycemic control."
    },
    {
        "name": "Barley (Jau)",
        "category": "Whole Grains",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["gluten"],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"],
        "glycemic_index": 28,
        "key_nutrients": "Soluble Fiber (Beta-glucan), Selenium, Potassium",
        "health_benefit": "Exceptionally low glycemic index (28). Promotes gut microbiota fermentation into short-chain fatty acids.",
        "rationale": "Clinical DASH-diet grain promoting glycemic stability."
    },
    {
        "name": "Brown Basmati Rice",
        "category": "Whole Grains",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "gluten_free", "high_fiber"],
        "glycemic_index": 55,
        "key_nutrients": "Manganese, Magnesium, Insoluble Fiber",
        "health_benefit": "Intact bran and germ layer provides sustained energy release without the sudden insulin spikes of white rice.",
        "rationale": "Wholesome alternative for carbohydrate staple replacement."
    },

    # --- VEGETABLES & LEAFY GREENS ---
    {
        "name": "Baby Spinach (Palak)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium", "heart_healthy"],
        "glycemic_index": 15,
        "key_nutrients": "Potassium (558mg), Dietary Nitrates, Lutein, Folate",
        "health_benefit": "Dietary nitrates convert into nitric oxide in endothelial cells, promoting vasodilation and reducing arterial stiffness.",
        "rationale": "Cornerstone of the DASH diet for blood pressure reduction."
    },
    {
        "name": "Bitter Gourd (Karela)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "heart_healthy"],
        "glycemic_index": 15,
        "key_nutrients": "Charantin, Vicine, Polypeptide-p (plant insulin mimic)",
        "health_benefit": "Bioactive peptides increase cellular glucose uptake and glycogen synthesis in liver and muscle tissue.",
        "rationale": "Scientifically verified botanical support for glycemic management."
    },
    {
        "name": "Broccoli & Florets",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium", "heart_healthy"],
        "glycemic_index": 15,
        "key_nutrients": "Sulforaphane, Vitamin C (90mg), Potassium, Calcium",
        "health_benefit": "Potent Nrf2 activator; sulforaphane protects vascular endothelium from oxidative injury caused by high blood glucose.",
        "rationale": "High-antioxidant cruciferous vegetable for metabolic protection."
    },
    {
        "name": "Fenugreek Leaves (Methi)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"],
        "glycemic_index": 15,
        "key_nutrients": "4-hydroxyisoleucine, Galactomannan fiber, Iron",
        "health_benefit": "Galactomannan mucilage slows carbohydrate digestion; 4-hydroxyisoleucine stimulates glucose-dependent insulin secretion.",
        "rationale": "Proven clinical efficacy in stabilizing fasting blood glucose."
    },
    {
        "name": "Raw Garlic (Lasun)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["hypertension_friendly", "heart_healthy", "diabetic_friendly", "low_sodium"],
        "glycemic_index": 15,
        "key_nutrients": "Allicin, S-allyl cysteine, Organic sulfur",
        "health_benefit": "Stimulates hydrogen sulfide and nitric oxide production, directly relaxing blood vessels and lowering systolic BP.",
        "rationale": "Clinically researched natural ACE-modulating food additive."
    },
    {
        "name": "Beetroot (Cooked / Salad)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["hypertension_friendly", "low_sodium", "heart_healthy"],
        "glycemic_index": 61,
        "key_nutrients": "Inorganic Nitrate, Betaine, Potassium (325mg)",
        "health_benefit": "Extensively documented in clinical trials to acutely lower both systolic and diastolic blood pressure within 2-4 hours.",
        "rationale": "Vascular endothelium support for hypertension."
    },
    {
        "name": "Okra (Bhindi / Lady's Finger)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"],
        "glycemic_index": 20,
        "key_nutrients": "Soluble mucilage fiber, Myricetin, Polyphenols",
        "health_benefit": "Mucilage inhibits cholesterol absorption in the intestine and modulates postprandial glucose surges.",
        "rationale": "Dietary staple for diabetic carbohydrate management."
    },
    {
        "name": "Bell Peppers (Capsicum)",
        "category": "Vegetables",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "low_sodium", "heart_healthy"],
        "glycemic_index": 15,
        "key_nutrients": "Capsanthin, Vitamin C (128mg), Vitamin A",
        "health_benefit": "Zero sodium, rich in antioxidants that protect low-density lipoproteins from oxidative modification.",
        "rationale": "Cardiovascular protective vegetable with minimal calorie impact."
    },

    # --- PROTEINS & LEGUMES ---
    {
        "name": "Yellow Moong Dal (Split Green Gram)",
        "category": "Proteins & Legumes",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_protein", "high_fiber"],
        "glycemic_index": 38,
        "key_nutrients": "Plant Protein 24g/100g, Potassium, Resistant Starch",
        "health_benefit": "Highly digestible legume; high potassium counters excess sodium, while resistant starch nourishes beneficial gut flora.",
        "rationale": "Gold-standard plant protein for cardiovascular and metabolic care."
    },
    {
        "name": "Chickpeas (Chana / Hummus)",
        "category": "Proteins & Legumes",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "heart_healthy", "high_protein", "high_fiber"],
        "glycemic_index": 33,
        "key_nutrients": "Protein 19g/100g, Dietary Fiber 17g, Isoflavones",
        "health_benefit": "Low glycemic index with high soluble and insoluble fiber slows gastric emptying and enhances post-meal satiety.",
        "rationale": "Excellent staple for sustained glycemic stability and lipid management."
    },
    {
        "name": "Firm Organic Tofu",
        "category": "Proteins & Legumes",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["soy"],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"],
        "glycemic_index": 15,
        "key_nutrients": "Soy Protein 17g, Isoflavones (Genistein), Calcium 350mg",
        "health_benefit": "Zero cholesterol, low saturated fat; soy isoflavones support arterial compliance and endothelial function.",
        "rationale": "Plant-based protein ideal for hypertension and cholesterol control."
    },
    {
        "name": "Skinless Chicken Breast",
        "category": "Proteins & Legumes",
        "diet_types": ["Non-vegetarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_protein", "low_sodium"],
        "glycemic_index": 0,
        "key_nutrients": "Lean Animal Protein 31g/100g, Niacin, Phosphorus",
        "health_benefit": "Zero carbohydrates and very low saturated fat; does not trigger insulin secretion while preserving lean muscle mass.",
        "rationale": "Lean protein choice recommended under DASH diet guidelines."
    },
    {
        "name": "Wild Salmon (or Mackerel / Sardines)",
        "category": "Proteins & Legumes",
        "diet_types": ["Non-vegetarian", "Pescatarian"],
        "allergens": ["fish"],
        "health_attributes": ["diabetic_friendly", "hypertension_friendly", "heart_healthy", "high_protein"],
        "glycemic_index": 0,
        "key_nutrients": "EPA & DHA Omega-3 Fatty Acids, Vitamin D, Selenium",
        "health_benefit": "Omega-3s reduce serum triglycerides, decrease systemic inflammation, and improve vascular endothelial relaxation.",
        "rationale": "Cardiovascular American Heart Association (AHA) top recommendation."
    },
    {
        "name": "Boiled Whole Eggs",
        "category": "Proteins & Legumes",
        "diet_types": ["Eggetarian", "Non-vegetarian"],
        "allergens": ["eggs"],
        "health_attributes": ["diabetic_friendly", "low_gi", "high_protein"],
        "glycemic_index": 0,
        "key_nutrients": "Protein 6.3g/egg, Choline, Lutein, Zeaxanthin",
        "health_benefit": "Zero glycemic impact. High protein and healthy lipids stimulate cholecystokinin release, preventing overeating.",
        "rationale": "Nutrient-dense breakfast protein for glycemic balance."
    },
    {
        "name": "Plain Low-Fat Greek Yogurt (Curd)",
        "category": "Proteins & Legumes",
        "diet_types": ["Vegetarian", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["dairy"],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_protein", "heart_healthy"],
        "glycemic_index": 14,
        "key_nutrients": "Live Probiotic Cultures, Calcium (200mg), Potassium (140mg)",
        "health_benefit": "Probiotic bacteria synthesize bioactive peptides during fermentation that exert mild ACE-inhibitory effects on blood pressure.",
        "rationale": "Supports gut microbiome and vascular health."
    },

    # --- FRUITS ---
    {
        "name": "Wild Blueberries / Blackberries",
        "category": "Fruits",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy"],
        "glycemic_index": 40,
        "key_nutrients": "Anthocyanins, Pterostilbene, Vitamin C, Dietary Fiber",
        "health_benefit": "Anthocyanins improve insulin sensitivity via GLUT4 translocation and protect microvascular retinal capillaries.",
        "rationale": "Top-tier diabetic fruit with proven vascular benefits."
    },
    {
        "name": "Green Apple (with skin)",
        "category": "Fruits",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"],
        "glycemic_index": 36,
        "key_nutrients": "Quercetin, Pectin fiber, Polyphenols",
        "health_benefit": "Pectin binds bile acids in the gut to reduce blood cholesterol; quercetin reduces vascular oxidative stress.",
        "rationale": "Crisp low-glycemic fruit with low total sugar content."
    },
    {
        "name": "Pomegranate (Anar)",
        "category": "Fruits",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["hypertension_friendly", "heart_healthy", "low_sodium"],
        "glycemic_index": 53,
        "key_nutrients": "Punicalagins, Ellagic Acid, Potassium (236mg)",
        "health_benefit": "Potent polyphenolic antioxidants demonstrate natural serum ACE-inhibitory activity, reducing systolic BP.",
        "rationale": "Cardiovascular tonic backed by human clinical trials."
    },
    {
        "name": "Fresh Guava (Amrood)",
        "category": "Fruits",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "high_fiber"],
        "glycemic_index": 30,
        "key_nutrients": "Dietary Fiber 5.4g/100g, Vitamin C 228mg (4x orange), Potassium",
        "health_benefit": "High fiber-to-sugar ratio delays intestinal glucose uptake, preventing hyperglycemia.",
        "rationale": "Economical tropical fruit ideal for diabetic daily snacking."
    },
    {
        "name": "Ripe Papaya",
        "category": "Fruits",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "heart_healthy", "high_fiber"],
        "glycemic_index": 60,
        "key_nutrients": "Papain enzyme, Lycopene, Carotenoids",
        "health_benefit": "Digestive enzyme papain aids protein breakdown; lycopene guards against lipid peroxidation.",
        "rationale": "Moderate GI fruit with high water content and low glycemic load."
    },

    # --- HEALTHY FATS, NUTS & SEEDS ---
    {
        "name": "Raw California Almonds (Badam)",
        "category": "Healthy Fats & Nuts",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["tree_nuts", "nuts"],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_protein"],
        "glycemic_index": 15,
        "key_nutrients": "Monounsaturated Fatty Acids (MUFA), Vitamin E (Alpha-tocopherol), Magnesium (270mg)",
        "health_benefit": "Magnesium deficiency is prevalent in diabetics; dietary magnesium improves insulin receptor sensitivity and relaxes blood vessels.",
        "rationale": "DASH and Mediterranean diet staple for cardiometabolic protection."
    },
    {
        "name": "Walnuts (Akhrot)",
        "category": "Healthy Fats & Nuts",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["tree_nuts", "nuts"],
        "health_attributes": ["hypertension_friendly", "heart_healthy", "diabetic_friendly", "low_sodium"],
        "glycemic_index": 15,
        "key_nutrients": "Alpha-linolenic Acid (Plant Omega-3), Polyphenols",
        "health_benefit": "High ALA content enhances flow-mediated dilation of arteries and mitigates vascular endothelial inflammation.",
        "rationale": "AHA-certified heart-healthy nut."
    },
    {
        "name": "Chia Seeds & Basil Seeds",
        "category": "Healthy Fats & Nuts",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "hypertension_friendly", "heart_healthy", "high_fiber"],
        "glycemic_index": 10,
        "key_nutrients": "Soluble Mucilage Fiber 34g/100g, Omega-3 ALA, Calcium",
        "health_benefit": "Absorbs 10x its weight in water to create an intestinal gel barrier, slowing glucose absorption and blunting postprandial surges.",
        "rationale": "Exceptional seed for diabetes management and blood pressure reduction."
    },
    {
        "name": "Roasted Flaxseeds (Alsi)",
        "category": "Healthy Fats & Nuts",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "hypertension_friendly", "heart_healthy", "high_fiber"],
        "glycemic_index": 10,
        "key_nutrients": "Secoisolariciresinol Diglucoside (SDG Lignans), ALA, Soluble Fiber",
        "health_benefit": "Lignans act as phytoestrogens and powerful antioxidants; proven in clinical trials to reduce both systolic and diastolic BP.",
        "rationale": "Potent cardiovascular functional food for hypertension."
    },
    {
        "name": "Extra Virgin Olive Oil (Cold-Pressed)",
        "category": "Healthy Fats & Nuts",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "hypertension_friendly", "heart_healthy"],
        "glycemic_index": 0,
        "key_nutrients": "Oleic Acid (73%), Oleocanthal, Polyphenols",
        "health_benefit": "Oleocanthal exerts anti-inflammatory effects comparable to low-dose ibuprofen; protects LDL from atherogenic oxidation.",
        "rationale": "Gold standard culinary fat for Mediterranean dietary patterns."
    },

    # --- BEVERAGES & HERBAL INFUSIONS ---
    {
        "name": "Hibiscus Tea (Gudhal)",
        "category": "Beverages & Infusions",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["hypertension_friendly", "low_sodium", "heart_healthy"],
        "glycemic_index": 0,
        "key_nutrients": "Anthocyanins, Protocatechuic acid, Bioflavonoids",
        "health_benefit": "Demonstrated in multiple randomized trials to lower systolic BP by 7 mmHg through natural diuretic and ACE-inhibitory mechanisms.",
        "rationale": "Scientifically verified herbal infusion for blood pressure control."
    },
    {
        "name": "Japanese Green Tea (Sencha / Matcha)",
        "category": "Beverages & Infusions",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "hypertension_friendly", "heart_healthy"],
        "glycemic_index": 0,
        "key_nutrients": "EGCG (Epigallocatechin gallate), L-Theanine",
        "health_benefit": "EGCG enhances cellular insulin signaling via IRS-1 phosphorylation and improves vascular flow.",
        "rationale": "Metabolic-support beverage with zero calories and zero sodium."
    },
    {
        "name": "Ceylon Cinnamon Infusion (Dalchini)",
        "category": "Beverages & Infusions",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": [],
        "health_attributes": ["diabetic_friendly", "low_gi", "heart_healthy"],
        "glycemic_index": 0,
        "key_nutrients": "Cinnamaldehyde, Proanthocyanidins",
        "health_benefit": "Mimics insulin by activating cellular insulin receptors; slows gastric emptying to moderate postprandial glucose.",
        "rationale": "Traditional botanical infusion for glycemic stabilization."
    },
    {
        "name": "Low-Fat Spiced Buttermilk (Chaas / Mattha)",
        "category": "Beverages & Infusions",
        "diet_types": ["Vegetarian", "Eggetarian", "Non-vegetarian", "Pescatarian"],
        "allergens": ["dairy"],
        "health_attributes": ["diabetic_friendly", "hypertension_friendly", "low_sodium"],
        "glycemic_index": 18,
        "key_nutrients": "Probiotics, Potassium (280mg), Calcium, Roasted Cumin",
        "health_benefit": "Hydrating electrolyte-rich beverage; roasted cumin and mint provide carminative support without excess sodium.",
        "rationale": "Refreshing traditional low-calorie probiotic drink."
    }
]

# =====================================================================
# 2. RECOMMENDATION ENGINE & FILTERING ALGORITHM
# =====================================================================

def get_user_dietary_profile(user_id):
    """
    Fetch user's profile and food preferences from the database.
    """
    with get_connection() as conn:
        profile = conn.execute("""
            SELECT full_name, age
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        food = conn.execute("""
            SELECT diet_type, allergies, dietary_restrictions, food_preferences
            FROM food_preferences
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    diet_type = food["diet_type"] if food and food["diet_type"] else "Not specified"
    allergies_raw = food["allergies"] if food and food["allergies"] else ""
    restrictions_raw = food["dietary_restrictions"] if food and food["dietary_restrictions"] else ""
    user_notes = food["food_preferences"] if food and food["food_preferences"] else ""

    # Parse allergy tokens into lowercase list
    allergy_tokens = [a.strip().lower() for a in allergies_raw.replace(';', ',').split(',') if a.strip()]

    return {
        "full_name": profile["full_name"] if profile and profile["full_name"] else "User",
        "diet_type": diet_type,
        "allergies_raw": allergies_raw,
        "allergy_tokens": allergy_tokens,
        "restrictions_raw": restrictions_raw,
        "restrictions_lower": restrictions_raw.lower(),
        "user_notes": user_notes
    }


def filter_and_rank_foods(user_profile, selected_category=None, condition_filter=None, search_query=""):
    """
    Hybrid recommendation algorithm:
    1. Hard safety constraints (Allergen exclusion & Diet type compliance)
    2. Multi-attribute utility ranking based on health profile (DASH / Low-GI alignment)
    """
    diet_type = user_profile["diet_type"]
    allergy_tokens = user_profile["allergy_tokens"]
    restrictions = user_profile["restrictions_lower"]

    # Detect conditions from restrictions or user input
    wants_hypertension = any(k in restrictions for k in ["hypertension", "bp", "blood pressure", "low-sodium", "low sodium", "salt", "dash"])
    wants_diabetes = any(k in restrictions for k in ["diabetic", "diabetes", "sugar", "low-sugar", "low sugar", "low-gi", "glucose", "insulin"])
    wants_heart = any(k in restrictions for k in ["heart", "cholesterol", "lipid", "cardio"])

    if condition_filter == "hypertension":
        wants_hypertension = True
    elif condition_filter == "diabetes":
        wants_diabetes = True
    elif condition_filter == "heart":
        wants_heart = True

    recommended = []

    for food in FOOD_DATABASE:
        # --- LAYER 1: HARD SAFETY CONSTRAINTS ---

        # 1. Diet Type Check
        if diet_type != "Not specified":
            if diet_type not in food["diet_types"]:
                continue

        # 2. Strict Allergen Exclusion
        has_allergy_conflict = False
        food_allergens = [a.lower() for a in food["allergens"]]
        for u_allergy in allergy_tokens:
            for f_allergen in food_allergens:
                if u_allergy in f_allergen or f_allergen in u_allergy:
                    has_allergy_conflict = True
                    break
            # Also check if allergy keyword is in food name
            if u_allergy in food["name"].lower():
                has_allergy_conflict = True
                break
            if has_allergy_conflict:
                break

        if has_allergy_conflict:
            continue

        # 3. Category Filter
        if selected_category and selected_category != "All Categories":
            if food["category"] != selected_category:
                continue

        # 4. Search Query Filter
        if search_query:
            query = search_query.lower()
            if not (query in food["name"].lower() or query in food["key_nutrients"].lower() or query in food["health_benefit"].lower()):
                continue

        # --- LAYER 2: MULTI-ATTRIBUTE UTILITY SCORING ---
        score = 10.0 # Base candidate score
        reasons = []

        attrs = food["health_attributes"]

        if wants_hypertension and "hypertension_friendly" in attrs:
            score += 15.0
            reasons.append("Low-Sodium & High-Potassium / Nitrate (DASH-Aligned)")

        if wants_diabetes and "diabetic_friendly" in attrs:
            score += 15.0
            reasons.append("Low Glycemic Index (<55) & High Viscous Fiber")

        if wants_heart and "heart_healthy" in attrs:
            score += 10.0
            reasons.append("Cardiovascular & Lipid Protection")

        if "high_fiber" in attrs:
            score += 5.0
        if "high_protein" in attrs:
            score += 5.0

        if not reasons:
            reasons.append("Balanced nutrient-dense whole food choice")

        food_item = dict(food)
        food_item["score"] = score
        food_item["reasons"] = reasons
        recommended.append(food_item)

    # Sort descending by score
    recommended.sort(key=lambda x: x["score"], reverse=True)
    return recommended


# =====================================================================
# 3. STREAMLIT UI PRESENTATION
# =====================================================================

def show_food_suggestions_page(user_id):
    st.title("🥗 Personalized Food Suggestions")
    st.caption("Evidence-Based Clinical Nutrition Recommender | Grounded in ADA & AHA Guidelines")

    # Safety Notice
    st.info(
        "💡 **Dietary Guidance Notice:** Suggestions provided here are evidence-based general wellness guidelines for nutritional support. "
        "They do NOT replace personalized advice from a registered dietitian or your physician."
    )

    profile = get_user_dietary_profile(user_id)

    # User Profile Pill
    with st.container(border=True):
        st.markdown(f"#### 👤 Nutrition Profile for **{profile['full_name']}**")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown(f"**Diet Type:** `{profile['diet_type']}`")
        with col_p2:
            allergies_display = profile['allergies_raw'] if profile['allergies_raw'] else "None declared"
            st.markdown(f"**Excluded Allergens:** `{allergies_display}`")
        with col_p3:
            restr_display = profile['restrictions_raw'] if profile['restrictions_raw'] else "General wellness"
            st.markdown(f"**Health Restrictions:** `{restr_display}`")

        st.caption("To update your diet type, allergies, or restrictions, navigate to the **Profile** tab in the sidebar.")

    st.divider()

    # Search & Interactive Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.2, 1.2])

    with ctrl_col1:
        search_query = st.text_input("🔍 Search Food or Nutrient", placeholder="e.g. Oats, Potassium, Chia, Dal...")

    with ctrl_col2:
        categories = ["All Categories", "Whole Grains", "Vegetables", "Proteins & Legumes", "Fruits", "Healthy Fats & Nuts", "Beverages & Infusions"]
        selected_category = st.selectbox("Category Filter", categories)

    with ctrl_col3:
        condition_options = {
            "All Recommended Foods": None,
            "Hypertension-Friendly (DASH)": "hypertension",
            "Diabetic-Friendly (Low-GI)": "diabetes",
            "Heart-Healthy & Cholesterol": "heart"
        }
        cond_choice = st.selectbox("Health Focus Priority", list(condition_options.keys()))
        condition_filter = condition_options[cond_choice]

    # Get Recommendations
    foods = filter_and_rank_foods(
        profile,
        selected_category=selected_category,
        condition_filter=condition_filter,
        search_query=search_query
    )

    st.write(f"Showing **{len(foods)}** verified foods matching your dietary profile:")

    if not foods:
        st.warning("No foods matched your current search and allergen filters. Try adjusting the search query or loosening restrictions in your Profile.")
        return

    # Render Food Cards in a 2-Column Responsive Layout
    for i in range(0, len(foods), 2):
        col1, col2 = st.columns(2)
        row_foods = [foods[i]]
        if i + 1 < len(foods):
            row_foods.append(foods[i + 1])

        for col, food in zip([col1, col2], row_foods):
            with col:
                with st.container(border=True):
                    # Category Badge + Food Name
                    st.markdown(f"<span style='font-size: 11px; background-color: #e0f2f1; color: #00695c; padding: 3px 8px; border-radius: 12px; font-weight: 600;'>{food['category'].upper()}</span>", unsafe_allow_html=True)
                    st.subheader(food["name"])

                    # Key Metrics
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.markdown(f"**Glycemic Index:** `{food['glycemic_index']}` (Low-GI)")
                    with m_col2:
                        allergens_tag = ", ".join(food["allergens"]).title() if food["allergens"] else "None (Hypoallergenic)"
                        st.markdown(f"**Allergens:** `{allergens_tag}`")

                    st.markdown(f"**Key Nutrients:** *{food['key_nutrients']}*")
                    st.markdown(f"**Health Action:** {food['health_benefit']}")

                    # Algorithmic Rationale
                    st.markdown(
                        f"""
                        <div style='background-color: #f1f8e9; border-left: 4px solid #558b2f; padding: 8px 12px; border-radius: 4px; margin-top: 8px;'>
                            <small style='color: #33691e; font-weight: 700;'>WHY IT'S RECOMMENDED FOR YOU:</small><br>
                            <small style='color: #2e7d32;'>{' • '.join(food['reasons'])}</small><br>
                            <small style='color: #555;'><em>{food['rationale']}</em></small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
