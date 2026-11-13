"""
MediAssist AI - Clinical Dietary & Nutrition Chatbot (Hybrid Architecture)
-------------------------------------------------------------------------
Conversational dietary agent supporting two seamless modes:
1. 100% Local Offline CDS Engine:
   - ICMR-NIN Indian Food Composition Tables (567 authentic foods)
   - Popular prepared Indian dishes (Khichdi, Idli, Dosa, Poha, Upma, Roti, Jaggery, etc.)
   - Pharmacological mechanisms (CYP3A4, GI tolerance, nocturnal cholesterol synthesis)
   - Symptom & digestion support (acidity, bloating, postprandial fatigue)
   - Strict allergen elimination & comorbidity safety rules
2. Optional Google Gemini API (Free Tier):
   - Open-ended conversational reasoning grounded in the patient's medical history
   - Zero additional dependencies (uses standard requests library)
"""

import os
import json
import re
from pathlib import Path
import requests
import streamlit as st

from database import get_connection, get_user_comorbidities
import medicine_food_integration as mfi
from food_suggestions import get_user_dietary_profile, load_food_database, filter_and_rank_foods


# =============================================================================
# 1. OPTIONAL GOOGLE GEMINI API CONNECTOR
# =============================================================================

def call_gemini_api(api_key, user_message, patient_context, chat_history=None):
    """
    Calls Google Gemini REST API (gemini-1.5-flash) using standard requests.
    Grounded with the patient's exact clinical profile and medication safety rules.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    comorbs_str = ", ".join(patient_context.get("comorbidity_names", [])) or "None declared"
    meds_str = ", ".join([f"{m['db_name']} ({m.get('dosage', '')})" for m in patient_context.get("active_profiles", [])]) or "None"
    allergies_str = patient_context.get("allergies_raw", "None") or "None declared"
    diet_type = patient_context.get("diet_type", "Vegetarian")

    system_instruction = f"""You are MediAssist AI, an expert, empathetic Clinical Dietitian and Medical Nutrition Specialist.
You are counseling patient {patient_context.get('full_name', 'Patient')} (Age {patient_context.get('age', 55)}).

CRITICAL PATIENT CLINICAL PROFILE:
- Diet Type: {diet_type} (Strictly respect this: if Vegetarian, NEVER suggest meat, poultry, fish, or eggs!)
- Declared Food Allergies: {allergies_str} (STRICT SAFETY DIRECTIVE: NEVER recommend or include any food containing these allergens!)
- Diagnosed Medical Conditions: {comorbs_str}
- Active Prescriptions: {meds_str}

CORE CLINICAL RULES & DRUG INTERACTIONS:
1. If patient is on Amlodipine or Atorvastatin: STRICTLY CONTRAINDICATE Grapefruit and Pomelo juice (inhibits intestinal CYP3A4, causing drug accumulation and toxicity).
2. If patient is on Metformin: Emphasize taking with meals to prevent GI upset, and highlight synergies with soluble fiber / low-GI foods.
3. If patient has Diabetes: Prioritize Low Glycemic Index (<55) and high fiber foods; strictly caution against jaggery, honey, refined flour (maida), and simple sweets.
4. If patient has Hypertension: Reinforce DASH guidelines (cap sodium < 2000mg/day, encourage natural potassium if kidneys are healthy).
5. Ground your recommendations in authentic Indian foods and ICMR-NIN guidelines (millets like Ragi/Bajra/Jowar, whole pulses like Moong/Chana, green leafy vegetables).
6. Keep responses practical, compassionate, formatted with clear bullet points and markdown bold headers. Avoid overwhelming walls of text."""

    contents = []

    # Include recent turns for conversational continuity
    if chat_history:
        for msg in chat_history[-4:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

    # Current user turn with injected system prompt context
    contents.append({
        "role": "user",
        "parts": [{"text": f"[Clinical Context & Safety Rules: {system_instruction}]\n\nPatient Question: {user_message}"}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 800
        }
    }

    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                return candidates[0]["content"]["parts"][0]["text"]
            return "I received an empty response from the AI model. Please try asking again."
        elif resp.status_code == 400:
            return f"⚠️ **Gemini API Error (400):** Invalid API key or request format. Please check your API key in the settings panel below."
        elif resp.status_code == 429:
            return "⏳ **Gemini API Rate Limit Exceeded:** Free tier rate limit reached. Falling back to the local offline clinical engine for this query."
        else:
            return f"⚠️ **Gemini API Error ({resp.status_code}):** {resp.text[:200]}"
    except requests.exceptions.Timeout:
        return "⏱️ **Network Timeout:** The external AI request timed out. Please check your connection or switch to the local offline engine."
    except Exception as e:
        return f"⚠️ **AI Service Error:** {str(e)}"


# =============================================================================
# 2. LOCAL CLINICAL DIETARY ASSISTANT (100% OFFLINE)
# =============================================================================

class ClinicalDietaryAssistant:
    """Intelligent local conversational agent for personalized medical nutrition therapy."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.profile = get_user_dietary_profile(user_id)
        self.analysis = mfi.analyze_user_food_drug_interactions(user_id)
        self.active_profiles = self.analysis.get("active_profiles", [])
        self.foods = load_food_database()
        self.comorbidities = set(self.profile.get("comorbidities", []))
        self.allergies = self.profile.get("allergy_tokens", [])
        self.diet_type = self.profile.get("diet_type", "Not specified")

    # -------------------------------------------------------------------------
    # FOOD ENTITY SEARCH & PREPARED DISH MAPPING
    # -------------------------------------------------------------------------
    def find_food_in_query(self, query):
        """Identifies raw food or mapped authentic Indian item in user query."""
        q_clean = query.lower()
        for ch in ["?", "!", ",", ".", "(", ")", "/", "'", '"']:
            q_clean = q_clean.replace(ch, " ")

        tokens = [t.strip() for t in q_clean.split() if len(t.strip()) > 2]

        stopwords = {
            "can", "eat", "drink", "have", "take", "safe", "good", "bad", "with", "for", "the",
            "and", "should", "avoid", "suggest", "recommend", "best", "what", "which", "about",
            "food", "diet", "meal", "health", "healthy", "daily", "okay", "today", "please",
            "medicine", "medicines", "tablet", "tablets", "morning", "night", "dinner", "lunch",
            "water", "much", "many", "how", "better"
        }
        tokens = [t for t in tokens if t not in stopwords]

        alias_map = {
            "coconut water": "tender coconut water",
            "nariyal pani": "tender coconut water",
            "green tea": "green tea",
            "rolled oats": "rolled oats",
            "oats": "steel-cut oats",
            "oatmeal": "steel-cut oats",
            "ragi": "finger millet",
            "nachni": "finger millet",
            "bajra": "pearl millet",
            "jowar": "sorghum",
            "palak": "spinach",
            "spinach": "spinach",
            "methi": "fenugreek",
            "fenugreek": "fenugreek",
            "curd": "curd / dahi",
            "dahi": "curd / dahi",
            "yogurt": "curd / dahi",
            "buttermilk": "buttermilk",
            "chaas": "buttermilk",
            "paneer": "paneer",
            "moong": "moong",
            "mung": "moong",
            "chana": "chana",
            "chickpea": "bengal gram",
            "rajma": "kidney beans",
            "dal": "lentil",
            "grapefruit": "grapefruit",
            "chakotra": "grapefruit",
            "pomelo": "grapefruit",
            "banana": "banana",
            "kela": "banana",
            "apple": "apple",
            "seb": "apple",
            "guava": "guava",
            "amrood": "guava",
            "papaya": "papaya",
            "papita": "papaya",
            "mango": "mango",
            "aam": "mango",
            "peanuts": "peanuts",
            "peanut": "peanuts",
            "mungfali": "peanuts",
            "groundnut": "peanuts",
            "tea": "tea",
            "chai": "tea",
            "coffee": "coffee",
            "walnuts": "walnut",
            "almonds": "almond",
            "badam": "almond",
            "makhana": "fox nuts",
            "fox nuts": "fox nuts",
            "karela": "bitter gourd",
            "bitter gourd": "bitter gourd",
            "lauki": "bottle gourd",
            "bottle gourd": "bottle gourd",
            "bhindi": "okra",
            "okra": "okra",
            "lady finger": "okra",
            "rice": "rice",
            "roti": "wheat",
            "chapati": "wheat"
        }

        # Check multi-word phrase in query first
        for phrase, target in alias_map.items():
            if phrase in q_clean:
                matches = self._search_foods(target)
                if matches:
                    return matches[0]

        # Check individual tokens
        for token in tokens:
            if token in alias_map:
                token = alias_map[token]
            matches = self._search_foods(token)
            if matches:
                return matches[0]

        return None

    def _search_foods(self, term):
        """Search food by name or local name in cached IFCT dataset."""
        term_lower = term.lower()
        exact = []
        partial = []
        for f in self.foods:
            f_name = f.get("name", "").lower()
            f_loc = f.get("local_name", "").lower()
            if term_lower == f_name or term_lower == f_loc:
                exact.append(f)
            elif term_lower in f_name or term_lower in f_loc:
                partial.append(f)
        return exact or partial

    # -------------------------------------------------------------------------
    # INTENT CLASSIFICATION
    # -------------------------------------------------------------------------
    def classify_intent(self, query):
        """Determines the clinical intent of the user query."""
        q = query.lower()

        # 1. Greetings
        if any(k in q for k in ["hi", "hello", "hey", "who are you", "help", "namaste", "good morning", "good evening"]):
            if len(q.split()) <= 4 and not any(w in q for w in ["eat", "food", "medicine", "safe", "why"]):
                return "GREETING"

        # 2. Pharmacology & "Why" Clinical Explanations
        if any(k in q for k in ["why", "how does", "explain", "mechanism", "interact", "reason"]):
            if "grapefruit" in q or "amlodipine" in q or "atorvastatin" in q or "statin" in q:
                return "WHY_GRAPEFRUIT_INTERACTION"
            if "metformin" in q and ("food" in q or "meal" in q or "stomach" in q):
                return "WHY_METFORMIN_WITH_FOOD"
            if "atorvastatin" in q and ("night" in q or "bedtime" in q):
                return "WHY_ATORVASTATIN_BEDTIME"

        # 3. Prepared Indian Dishes (Khichdi, Idli, Dosa, Poha, Upma, Roti, Jaggery, etc.)
        prepared_dishes = ["khichdi", "idli", "dosa", "poha", "upma", "chapati", "roti", "paratha",
                           "jaggery", "gur", "honey", "sugar", "sweets", "coffee", "chai", "tea", "salad", "paneer"]
        for dish in prepared_dishes:
            if dish in q:
                return f"PREPARED_DISH_{dish.upper()}"

        # 4. Comparative Queries (Oats vs Ragi, Brown vs White Rice)
        if any(w in q for w in ["vs", "compare", "better", "difference"]):
            if "oat" in q and "ragi" in q:
                return "COMPARE_OATS_RAGI"
            if "rice" in q and ("brown" in q or "white" in q):
                return "COMPARE_RICE"

        # 5. Symptom & Digestion Guidance
        if any(k in q for k in ["acidity", "acid reflux", "heartburn", "gerd", "burning in chest"]):
            return "SYMPTOM_ACIDITY"
        if any(k in q for k in ["bloating", "gas", "flatulence", "indigestion"]):
            return "SYMPTOM_BLOATING"
        if any(k in q for k in ["tired", "fatigue", "sleepy after eating", "lethargic"]):
            return "SYMPTOM_TIREDNESS"
        if any(k in q for k in ["constipation", "bowel", "stool"]):
            return "SYMPTOM_CONSTIPATION"

        # 6. Lifestyle Questions (Water, Hydration, Walking)
        if any(k in q for k in ["water", "hydration", "how much water", "drink water"]):
            return "LIFESTYLE_WATER"
        if any(k in q for k in ["exercise", "walking after meal", "walk after food", "walk after eating"]):
            return "LIFESTYLE_EXERCISE"

        # 7. Specific food entity with safety words
        food_mentioned = self.find_food_in_query(query)
        if food_mentioned and any(k in q for k in ["can i", "is it", "is ", "safe", "eat", "drink", "have", "okay", "take with", "consume", "avoid"]):
            return "FOOD_SAFETY"

        # 7. Drug interactions & medication inquiry
        med_keywords = ["interaction", "interactions", "medicine", "medication", "medicines", "medications",
                        "drug", "drugs", "tablet", "tablets", "pill", "prescription",
                        "metformin", "amlodipine", "atorvastatin", "timing", "empty stomach", "with meal", "with food"]
        if any(k in q for k in med_keywords) and any(w in q for w in ["what", "avoid", "safe", "timing", "interaction", "food", "clashes", "rules"]):
            return "DRUG_INTERACTIONS"

        # 8. Meal Planning
        if any(k in q for k in ["breakfast", "nashta", "morning meal"]):
            return "MEAL_BREAKFAST"
        if any(k in q for k in ["lunch", "afternoon meal", "dopahar"]):
            return "MEAL_LUNCH"
        if any(k in q for k in ["dinner", "raat ka khana", "evening meal"]):
            return "MEAL_DINNER"
        if any(k in q for k in ["snack", "snacks", "tea time", "evening snack"]):
            return "MEAL_SNACKS"
        if any(k in q for k in ["meal plan", "diet plan", "what to eat", "what should i eat", "menu"]):
            return "MEAL_PLAN"

        # 9. Nutrient Inquiries
        if any(k in q for k in ["high protein", "protein rich", "more protein"]):
            return "NUTRIENT_PROTEIN"
        if any(k in q for k in ["high fiber", "fiber rich", "more fiber"]):
            return "NUTRIENT_FIBER"
        if any(k in q for k in ["low sodium", "low salt", "salt free", "sodium"]):
            return "NUTRIENT_LOW_SODIUM"
        if any(k in q for k in ["low gi", "low glycemic", "glycemic index"]):
            return "NUTRIENT_LOW_GI"

        # 10. Disease Guidelines
        if any(k in q for k in ["diabetes", "diabetic", "sugar level", "blood sugar"]):
            return "DISEASE_DIABETES"
        if any(k in q for k in ["blood pressure", "hypertension", "bp", "dash"]):
            return "DISEASE_HYPERTENSION"
        if any(k in q for k in ["cholesterol", "lipid", "heart"]):
            return "DISEASE_CHOLESTEROL"
        if any(k in q for k in ["kidney", "ckd", "renal", "creatinine"]):
            return "DISEASE_CKD"
        if any(k in q for k in ["gout", "uric acid"]):
            return "DISEASE_GOUT"

        # 11. Lifestyle Questions
        if any(k in q for k in ["water", "hydration", "how much water"]):
            return "LIFESTYLE_WATER"
        if any(k in q for k in ["exercise", "walk", "walking after meal"]):
            return "LIFESTYLE_EXERCISE"

        if food_mentioned:
            return "FOOD_SAFETY"

        return "GENERAL_FALLBACK"

    # -------------------------------------------------------------------------
    # PREPARED INDIAN DISHES & RECIPES HANDLER
    # -------------------------------------------------------------------------
    def answer_prepared_dish(self, dish_key):
        """Clinical guidance for popular Indian prepared composite dishes."""
        p = self.profile
        is_diabetic = "diabetes" in self.comorbidities
        is_hypertensive = "hypertension" in self.comorbidities
        has_peanut_allergy = "peanuts" in self.allergies

        if dish_key == "KHICHDI":
            return (
                "### 🍲 Clinical Guidance: Moong Dal Khichdi\n"
                "> 🟢 **CLINICALLY RECOMMENDED (With Smart Recipe Tweaks)**\n\n"
                "**Why it's beneficial:**\n"
                "- **Complete Protein:** Rice lacks lysine, and lentils lack methionine; combining them provides all 9 essential amino acids.\n"
                "- **Gentle on Digestion:** Easily assimilated without mucosal irritation.\n\n"
                "**Tailored Advice for Your Profile:**\n"
                "- 🩺 **For Diabetes:** Traditional white rice khichdi can cause glucose spikes. Use a **2:1 ratio** (2 parts yellow moong dal to 1 part brown rice or broken wheat/daliya) and load with spinach (palak), bottle gourd (lauki), and carrots to increase soluble fiber.\n"
                "- 🧂 **For Blood Pressure:** Cook with a pinch of pink salt and temper with cumin (jeera) and hing (asafoetida) instead of heavy ghee."
            )
        elif dish_key in ["IDLI", "DOSA"]:
            return (
                f"### 🥞 Clinical Guidance: {dish_key.title()} & Sambar\n"
                "> 🟡 **SAFE WITH MODIFICATIONS (Watch Glycemic Index)**\n\n"
                "**Nutritional Analysis:**\n"
                "- **Fermentation Benefits:** Natural fermentation synthesizes B-complex vitamins and enhances mineral bioavailability.\n"
                "- ⚠️ **Glycemic Concern:** Traditional idli/dosa batter uses 3:1 polished white rice to urad dal, giving it a medium-high Glycemic Index (~65–70).\n\n"
                "**Recommended Variations:**\n"
                "- 🌟 **Ragi Idli / Ragi Dosa:** Finger millet batter lowers the GI to ~45 and adds 340mg of calcium.\n"
                "- 🌟 **Oats & Moong Dal Dosa (Pesarattu):** High viscous fiber blunts glucose surges.\n"
                "- 🍽️ **Smart Pairing:** Always pair with a large bowl of vegetable-rich sambar (extra drumsticks, tomatoes, and methi) to slow carbohydrate absorption."
            )
        elif dish_key == "POHA":
            warning_peanut = "\n- 🛑 **ALLERGY ALERT:** Do NOT add peanuts/groundnuts to your poha due to your declared peanut allergy! Substitute with roasted Bengal gram (chana) or sprouted moong." if has_peanut_allergy else ""
            return (
                "### 🥣 Clinical Guidance: Poha (Flattened Rice)\n"
                "> 🟡 **CONSUME WITH FIBER & PROTEIN ADDITIONS**\n\n"
                "**Nutritional Analysis:**\n"
                "- Poha is easily digestible and naturally rich in non-heme iron.\n"
                "- However, plain poha consists mostly of fast-digesting carbohydrates with low dietary fiber.\n\n"
                "**Optimization for Your Health Profile:**\n"
                f"- 🌿 **Add Fiber & Veggies:** Add generous amounts of green peas, onions, curry leaves, and grated carrots.{warning_peanut}\n"
                "- 🍋 **Vitamin C Synergy:** Squeeze fresh lemon juice over poha right before eating to double non-heme iron absorption."
            )
        elif dish_key == "UPMA":
            return (
                "### 🥣 Clinical Guidance: Upma\n"
                "> 🟡 **SAFE WITH GRAIN SUBSTITUTION**\n\n"
                "**Clinical Analysis:**\n"
                "- Traditional semolina (rava/sooji) is refined durum wheat with minimal fiber and a high glycemic index.\n\n"
                "**Healthier Diabetic & Cardio Alternatives:**\n"
                "- 🌾 **Broken Wheat (Daliya) Upma:** Rich in insoluble fiber, promoting slow, sustained glucose release.\n"
                "- 🌾 **Steel-Cut Rolled Oats Upma:** Provides Beta-Glucan fiber that actively helps lower your LDL cholesterol."
            )
        elif dish_key in ["ROTI", "CHAPATI", "PARATHA"]:
            return (
                "### 🫓 Clinical Guidance: Roti & Whole Grain Flatbreads\n"
                "> 🟢 **EXCELLENT STAPLE (Prefer Multigrain / Missi Roti)**\n\n"
                "**Clinical Recommendations:**\n"
                "- **100% Whole Wheat Roti:** Contains complex carbohydrates and magnesium.\n"
                "- 🌟 **Missi Roti (Diabetic Super-Choice):** Mix 70% whole wheat flour with 30% besan (chickpea flour) or chopped fenugreek (methi). This doubles the protein and soluble fiber, slashing the meal's glycemic impact.\n"
                "- ⚠️ **Avoid Plain Parathas:** Plain layered parathas shallow-fried in hydrogenated fats or vanaspati exacerbate dyslipidemia. Use dry-roasted rotis brushed lightly with cold-pressed mustard or olive oil."
            )
        elif dish_key in ["JAGGERY", "GUR", "HONEY", "SUGAR", "SWEETS"]:
            return (
                "### 🍯 Clinical Guidance: Jaggery (Gur), Honey & Sugar\n"
                "> 🔴 **STRICTLY RESTRICT / AVOID FOR TYPE 2 DIABETES**\n\n"
                "**The Medical Myth of Jaggery:**\n"
                "- Many people believe jaggery or honey is 'safe' for diabetes. **Medically, this is incorrect.**\n"
                "- Jaggery is ~85% sucrose and has a **Glycemic Index of 84+** (virtually identical to white refined sugar).\n"
                "- It causes rapid postprandial glucose spikes and triggers compensatory insulin resistance.\n\n"
                "**Safe Natural Alternatives:**\n"
                "- Flavor foods with natural sweet spices: Ceylon cinnamon (dalchini), green cardamom (elaichi), or nutmeg.\n"
                "- If you crave sweetness, have a small whole fruit (like guava or green apple) rather than processed sweets."
            )
        elif dish_key in ["TEA", "CHAI", "COFFEE"]:
            return (
                "### ☕ Clinical Guidance: Tea, Chai & Coffee\n"
                "> 🟡 **SAFE WITH TIMING & SUGAR RULES**\n\n"
                "**Medical Guidelines:**\n"
                "- **Zero Refined Sugar:** Always consume black or with a splash of low-fat cow's milk without added sugar or jaggery.\n"
                "- **Timing Rule:** Do NOT drink tea/coffee within 1 hour before or after meals or iron/calcium supplements. Polyphenols and tannins inhibit iron absorption by up to 75%.\n"
                "- **Blood Pressure Check:** Limit caffeine to 1–2 small cups daily; avoid strong caffeinated brews in the late evening to safeguard sleep architecture."
            )
        elif dish_key == "SALAD":
            return (
                "### 🥗 Clinical Guidance: Indian Raw Vegetable Salad\n"
                "> 🟢 **CLINICALLY RECOMMENDED (Pre-Meal Fiber Shield)**\n\n"
                "**The 'Fiber First' Principle:**\n"
                "- Eating a bowl of raw salad (cucumber, tomato, radish, grated carrot) **10 minutes before** your main meal creates a viscous gel matrix in the small intestine, slowing down glucose absorption by up to 35%.\n"
                "- 🧂 **Hypertension Tip:** Never sprinkle table salt or chaat masala over raw salad (a single pinch adds 200mg+ sodium!). Use freshly squeezed lemon juice and roasted jeera powder instead."
            )
        elif dish_key == "PANEER":
            return (
                "### 🧀 Clinical Guidance: Paneer (Cottage Cheese)\n"
                "> 🟢 **SAFE & HIGH PROTEIN (Prefer Low-Fat Cow Milk Paneer)**\n\n"
                "**Clinical Analysis:**\n"
                "- Zero glycemic index with high satiety and rich calcium (480mg/100g).\n"
                "- **Dyslipidemia Note:** Full-cream buffalo milk paneer is rich in saturated fatty acids. Choose paneer made from low-fat/toned cow's milk to protect your lipid profile while enjoying 18g of clean protein per 100g."
            )
        else:
            return self.recommend_meal("lunch")

    # -------------------------------------------------------------------------
    # PHARMACOLOGY & "WHY" EXPLANATIONS
    # -------------------------------------------------------------------------
    def answer_why_pharmacology(self, topic):
        """Deep scientific explanations for medication rules."""
        if topic == "WHY_GRAPEFRUIT_INTERACTION":
            return (
                "### 🔬 Pharmacological Mechanism: Grapefruit & CYP3A4\n"
                "> 🛑 **STRICT CONTRAINDICATION WITH AMLODIPINE & ATORVASTATIN**\n\n"
                "**How the interaction works:**\n"
                "1. **Intestinal Enzyme Blockade:** Grapefruit and pomelo contain potent natural furanocoumarins (*bergamottin* and *6',7'-dihydroxybergamottin*). These compounds permanently inhibit the **CYP3A4 enzyme** in your intestinal wall.\n"
                "2. **Excess Drug Floods the Bloodstream:** Normally, CYP3A4 breaks down ~50–60% of oral Amlodipine and Atorvastatin before they reach your circulation (first-pass metabolism).\n"
                "3. **Toxicity Risk:** With CYP3A4 disabled, drug blood levels can surge by **200% to 300%**, triggering severe orthostatic hypotension (dangerous blood pressure drops), severe ankle edema, or statin-induced muscle breakdown (*rhabdomyolysis*).\n\n"
                "💡 **Clinical Directive:** Strict avoidance of whole grapefruit, pomelo (chakotra), and citrus fruit blends containing them is mandatory while on your active prescriptions."
            )
        elif topic == "WHY_METFORMIN_WITH_FOOD":
            return (
                "### 🔬 Pharmacological Mechanism: Metformin Meal Timing\n"
                "> 💊 **TAKE WITH OR IMMEDIATELY AFTER MEALS**\n\n"
                "**Why food is required:**\n"
                "- **Gastrointestinal Irritation:** Metformin directly stimulates serotonin and GLP-1 release in the gut lining. On an empty stomach, this frequently causes cramping, nausea, metallic taste, and osmotic diarrhea.\n"
                "- **Mechanical Buffering:** Taking Metformin with meals mixes the medication with food, slowing stomach emptying and reducing GI side effects by over **80%**.\n"
                "- **Synergy with Fiber:** Soluble dietary fiber (from oats, methi, or dal) works alongside Metformin to stabilize postprandial glucose surges."
            )
        elif topic == "WHY_ATORVASTATIN_BEDTIME":
            return (
                "### 🔬 Pharmacological Mechanism: Atorvastatin Nocturnal Dosing\n"
                "> 🌙 **TAKE AT BEDTIME FOR OPTIMAL CHOLESTEROL CONTROL**\n\n"
                "**The Circadian Rhythm of Cholesterol:**\n"
                "- The liver enzyme **HMG-CoA Reductase** (which manufactures cholesterol) exhibits circadian rhythmicity, reaching **peak activity between midnight and 4:00 AM** when nutritional intake is absent.\n"
                "- Taking your statin in the evening ensures maximum drug availability in the liver during peak cholesterol synthesis hours."
            )

    # -------------------------------------------------------------------------
    # SYMPTOM & DIGESTION GUIDANCE
    # -------------------------------------------------------------------------
    def answer_symptoms(self, symptom):
        """Clinical dietary remedies for common digestive symptoms."""
        if symptom == "SYMPTOM_ACIDITY":
            return (
                "### 🩺 Clinical Guidance: Acidity & Acid Reflux (GERD)\n"
                "> 🌿 **SOOTHING MUCOSAL PROTECTION PROTOCOL**\n\n"
                "- 🥛 **Instant Soothers:** Half a cup of cold, low-fat cow's milk or a glass of fresh ash gourd (petha) or bottle gourd (lauki) juice coats and neutralizes gastric acid.\n"
                "- 🚫 **Strict Triggers to Avoid:** Raw green chilies, deep-fried snacks, vinegar, strong black coffee on an empty stomach, and acidic citrus.\n"
                "- ⏰ **Behavioral Rule:** Never lie down flat within 2.5 hours after eating. Elevate the head of your bed by 6 inches."
            )
        elif symptom == "SYMPTOM_BLOATING":
            return (
                "### 🩺 Clinical Guidance: Bloating & Gas Relief\n"
                "> 🌿 **CARMINATIVE DIGESTION TIPS**\n\n"
                "- 🫘 **Pulse Preparation:** Always soak whole pulses (rajma, chana, moong) for at least 6–8 hours and discard the soaking water before cooking to remove oligosaccharides.\n"
                "- 🌿 **Ayurvedic Carminatives:** Temper dals with cumin seeds (jeera), asafoetida (hing), and freshly grated ginger.\n"
                "- 🍵 **Post-Meal Sip:** Chew half a teaspoon of fennel seeds (saunf) or sip warm ajwain water after lunch."
            )
        elif symptom == "SYMPTOM_TIREDNESS":
            return (
                "### 🩺 Clinical Guidance: Post-Meal Fatigue (Food Coma)\n"
                "> 🩸 **PREVENTING POSTPRANDIAL GLUCOSE CRASHES**\n\n"
                "- **The Cause:** High-carbohydrate meals cause a rapid spike in blood glucose, prompting an exaggerated insulin response followed by reactive blood sugar drops (*reactive hypoglycemia*).\n"
                "- **The Solution:**\n"
                "  1. Reduce simple carbohydrates (white rice, white flour).\n"
                "  2. Follow the **Protein & Fiber First** rule: Eat salad and dal before touching rotis or rice.\n"
                "  3. Take a light 15-minute slow walk after meals to encourage skeletal muscle glucose uptake without insulin."
            )
        elif symptom == "SYMPTOM_CONSTIPATION":
            return (
                "### 🩺 Clinical Guidance: Constipation & Bowel Regularity\n"
                "> 🌾 **SOLUBLE FIBER & HYDRATION PROTOCOL**\n\n"
                "- 🌾 **Viscous Fiber:** Incorporate 1 teaspoon of Isabgol (psyllium husk) in a glass of warm water before bedtime.\n"
                "- 🍏 **Whole Fruits:** Guava (amrood) with seeds, papayas, and unpeeled apples contain pectin and insoluble cellulose that add healthy bulk to stools.\n"
                "- 💧 **Hydration:** Aim for 2.5 to 3 liters of water daily. Fiber cannot soften stools without adequate water intake."
            )

    # -------------------------------------------------------------------------
    # FOOD COMPARISONS
    # -------------------------------------------------------------------------
    def answer_comparison(self, comp_type):
        """Objective nutritional comparison between popular food staples."""
        if comp_type == "COMPARE_OATS_RAGI":
            return (
                "### ⚖️ Clinical Food Comparison: Steel-Cut Oats vs. Finger Millet (Ragi)\n\n"
                "| Nutritional Metric | Steel-Cut Rolled Oats | Finger Millet (Ragi) |\n"
                "| :--- | :--- | :--- |\n"
                "| **Glycemic Index** | Low (~53) | Low-Medium (~54–57) |\n"
                "| **Key Dietary Fiber** | **Beta-Glucan** (soluble) | Insoluble Fiber + Polyphenols |\n"
                "| **Calcium (per 100g)**| ~50 mg | **344 mg (7x higher!)** |\n"
                "| **Lipid Effect** | 🌟 Lowers LDL-Cholesterol | 🌟 Improves bone density |\n\n"
                "**Clinical Verdict for Your Profile:**\n"
                "- **Both are superstars!** Oats are superior for lowering LDL-cholesterol (great for your dyslipidemia), while Ragi provides unmatched calcium and antioxidant polyphenols. Alternate between them across the week for optimal balance."
            )
        elif comp_type == "COMPARE_RICE":
            return (
                "### ⚖️ Clinical Food Comparison: Brown Rice vs. Polished White Rice\n\n"
                "| Metric | Brown Basmati Rice | Polished White Rice |\n"
                "| :--- | :--- | :--- |\n"
                "| **Glycemic Index** | **~50–55 (Low/Medium)** | **~73 (High)** |\n"
                "| **Aleurone & Bran** | Intact (Rich in B-vitamins) | Stripped during milling |\n"
                "| **Fiber per 100g** | **3.5g (3x higher)** | ~1.0g |\n"
                "| **Magnesium** | 🌟 Supports insulin sensitivity| Minimal |\n\n"
                "**Clinical Verdict for Your Diabetes:**\n"
                "- Replace polished white rice with Brown Basmati or red rice. If white rice is consumed, pair it with twice the volume of dal and green vegetables to blunt the glycemic load."
            )

    # -------------------------------------------------------------------------
    # LIFESTYLE & HYDRATION
    # -------------------------------------------------------------------------
    def answer_lifestyle(self, topic):
        if topic == "LIFESTYLE_WATER":
            return (
                "### 💧 Hydration Guidelines for Cardiovascular & Metabolic Health\n"
                "- **Recommended Intake:** Aim for **2.5 to 3 liters** of clean water daily (approx. 8–10 glasses).\n"
                "- **Why it matters for you:** Proper hydration supports renal clearance, prevents hemoconcentration (which elevates blood pressure), and helps dietary fiber form a protective digestive gel.\n"
                "- 💡 *Tip: Keep a water bottle at your desk and sip regularly throughout the day; avoid drinking large volumes immediately before bedtime to prevent sleep disruptions.*"
            )
        elif topic == "LIFESTYLE_EXERCISE":
            return (
                "### 🚶 Exercise Timing & Post-Meal Movement\n"
                "- **The 'Post-Meal 15-Minute Walk':** Walking at a gentle pace for 10–15 minutes starting **20 minutes after meals** activates the GLUT-4 glucose transporters in skeletal muscle, clearing blood sugar without requiring extra insulin.\n"
                "- **Avoid Vigorous Strain:** Do not perform heavy weightlifting or high-intensity cardio immediately after eating; this diverts blood flow away from the digestive tract."
            )

    # -------------------------------------------------------------------------
    # MEAL PLANNING ENGINE
    # -------------------------------------------------------------------------
    def recommend_meal(self, meal_type="breakfast"):
        """Assembles a medically customized Indian meal plan honoring all health constraints."""
        meal_names = {
            "breakfast": "🍳 Personalized Breakfast Plan",
            "lunch": "🍛 Balanced Clinical Lunch Thali",
            "dinner": "🥗 Nourishing Low-Glycemic Dinner",
            "snacks": "🍵 Healthy Mid-Day & Evening Snacks"
        }
        title = meal_names.get(meal_type, "🥗 Curated Meal Suggestions")

        cat_priority = []
        if meal_type == "breakfast":
            cat_priority = ["Cereals and Millets", "Grain Legumes & Pulses", "Milk & Dairy Products", "Fruits"]
        elif meal_type in ["lunch", "dinner"]:
            cat_priority = ["Cereals and Millets", "Grain Legumes & Pulses", "Green Leafy Vegetables", "Other Vegetables"]
        elif meal_type == "snacks":
            cat_priority = ["Nuts and Oilseeds", "Grain Legumes & Pulses", "Fruits", "Beverages & Herbal Infusions"]

        ranked = filter_and_rank_foods(self.profile, active_profiles=self.active_profiles)

        selected = []
        used_cats = set()

        for f in ranked:
            if f.get("score", 0) < 0:
                continue
            cat = f.get("category", "")
            if cat in cat_priority and cat not in used_cats:
                selected.append(f)
                used_cats.add(cat)
            if len(selected) >= 4:
                break

        if len(selected) < 3:
            for f in ranked:
                if f not in selected and f.get("score", 0) > 0:
                    selected.append(f)
                if len(selected) >= 3:
                    break

        resp = [
            f"### {title}",
            f"Tailored specifically for **{self.profile['full_name']}** based on your **{self.diet_type}** diet, allergen safety, diagnosed conditions, and active prescriptions.",
            ""
        ]

        total_kcal = 0
        total_prot = 0
        total_fib = 0

        for idx, item in enumerate(selected, 1):
            name = item.get("name")
            local = item.get("local_name")
            display_title = f"{name} ({local})" if local else name
            cat = item.get("category", "")
            cal = item.get("energy_kcal", 0) or 0
            prot = item.get("protein_g", 0) or 0
            fib = item.get("dietary_fiber_g", 0) or 0
            gi = item.get("glycemic_index", "N/A")
            reasons = " &bull; ".join(item.get("reasons", [])[:2])

            if isinstance(cal, (int, float)):
                total_kcal += cal
            if isinstance(prot, (int, float)):
                total_prot += prot
            if isinstance(fib, (int, float)):
                total_fib += fib

            gi_tag = f" &bull; GI: `{gi}`" if gi != "N/A" else ""

            resp.append(f"**{idx}. {display_title}** `{cat}`")
            resp.append(f"- **Nutrition:** `{cal} kcal` &bull; Protein: `{prot}g` &bull; Fiber: `{fib}g`{gi_tag}")
            resp.append(f"- **Clinical Value:** {reasons}")
            resp.append("")

        resp.append(f"> 📊 **Meal Estimate:** ~`{total_kcal:.0f} kcal` &bull; **Protein:** ~`{total_prot:.1f}g` &bull; **Fiber:** ~`{total_fib:.1f}g`")
        resp.append("> 💡 *Tip: Maintain regular meal timings to help stabilize blood glucose and optimize medication absorption.*")

        return "\n".join(resp)

    # -------------------------------------------------------------------------
    # SPECIFIC FOOD SAFETY CHECK
    # -------------------------------------------------------------------------
    def evaluate_food_safety(self, food):
        """Deep clinical safety check of an IFCT food item."""
        name = food.get("name", "Unknown Food")
        local_name = food.get("local_name", "")
        category = food.get("category", "")
        full_title = f"{name} ({local_name})" if local_name else name

        verdicts = []
        risk_level = "safe"

        # Allergen check
        food_allergens = [a.lower() for a in food.get("allergens", [])]
        food_text = (name + " " + local_name + " " + category).lower()
        for u_allergy in self.allergies:
            if u_allergy and (u_allergy in food_allergens or u_allergy in food_text):
                risk_level = "allergy"
                verdicts.append(f"🛑 **DECLARED ALLERGEN CONFLICT:** You have a documented medical allergy to **{u_allergy.title()}**. Do NOT consume this food.")

        # Diet type check
        if self.diet_type != "Not specified":
            diet_compliant = self.diet_type in food.get("diet_types", [])
            if not diet_compliant:
                if risk_level != "allergy":
                    risk_level = "caution"
                verdicts.append(f"⚠️ **DIETARY PREFERENCE CONFLICT:** Classified as **{category}**, which is not aligned with your **{self.diet_type}** regimen.")

        # Medication contraindications
        drug_flags = mfi.evaluate_food_against_medications(food, self.active_profiles)
        for dflag in drug_flags:
            lvl = dflag.get("level")
            if lvl == "danger":
                risk_level = "danger"
                verdicts.append(f"🔴 **PRESCRIPTION CONTRAINDICATION ({dflag['title']}):** {dflag['detail']}")
            elif lvl == "warning":
                if risk_level not in ["danger", "allergy"]:
                    risk_level = "caution"
                verdicts.append(f"🟡 **MEDICATION PRECAUTION ({dflag['title']}):** {dflag['detail']}")
            elif lvl == "synergy" and risk_level not in ["danger", "allergy"]:
                verdicts.append(f"🌟 **THERAPEUTIC SYNERGY ({dflag['title']}):** {dflag['detail']}")

        if risk_level in ["danger", "allergy"]:
            verdicts = [v for v in verdicts if not v.startswith("🌟")]

        # Comorbidities
        attrs = food.get("health_attributes", [])
        gi = food.get("glycemic_index", "N/A")
        sod_mg = food.get("sodium_mg", 0) or 0
        pot_mg = food.get("potassium_mg", 0) or 0

        if "diabetes" in self.comorbidities:
            if isinstance(gi, (int, float)):
                if gi >= 70:
                    if risk_level not in ["danger", "allergy"]:
                        risk_level = "caution"
                    verdicts.append(f"⚠️ **High Glycemic Index (GI: {gi}):** Can cause rapid postprandial glucose spike. Restrict portion.")
                elif gi < 55:
                    verdicts.append(f"✅ **Low Glycemic Index (GI: {gi}):** Excellent for blood glucose stabilization.")
            elif "diabetic_friendly" in attrs or "low_gi" in attrs:
                verdicts.append("✅ **Diabetic-Friendly:** Rich in viscous dietary fiber, supporting HbA1c control.")

        if "hypertension" in self.comorbidities:
            if isinstance(sod_mg, (int, float)) and sod_mg > 150:
                if risk_level not in ["danger", "allergy"]:
                    risk_level = "caution"
                verdicts.append(f"⚠️ **Elevated Sodium ({sod_mg}mg/100g):** Restrict portion to keep daily sodium under DASH threshold (2,000 mg/day).")
            elif "low_sodium" in attrs or (isinstance(sod_mg, (int, float)) and sod_mg < 60):
                verdicts.append("✅ **Low-Sodium DASH Choice:** Safe for blood pressure management.")

            if "ckd" not in self.comorbidities and isinstance(pot_mg, (int, float)) and pot_mg >= 250:
                verdicts.append(f"🌿 **Potassium Rich ({pot_mg}mg/100g):** Helps counteract sodium and relaxes blood vessels.")

        if not verdicts:
            verdicts.append("✅ **ICMR-NIN Compliant:** Balanced Indian whole food with no contraindications detected for your health profile.")

        badge_map = {
            "safe": "🟢 **Clinically Safe & Recommended**",
            "caution": "🟡 **Consume with Caution & Portion Control**",
            "danger": "🔴 **Strictly Avoid / Contraindicated**",
            "allergy": "🛑 **ALLERGY CONTRAINDICATION**"
        }

        directive_map = {
            "safe": "> ✅ **CLINICAL ADVICE:** Excellent nutritional fit for your active health goals.",
            "caution": "> ⚠️ **CLINICAL ADVICE:** Allowed in measured portions or with specific spacing from medications.",
            "danger": "> 🛑 **SAFETY DIRECTIVE:** Strict clinical avoidance required. This item directly conflicts with your prescriptions or diagnoses.",
            "allergy": "> 🛑 **ALLERGY DIRECTIVE:** Strictly avoid. Cross-contamination risk must also be minimized."
        }

        resp = [
            f"### {badge_map.get(risk_level, '🟡 Evaluation')} : {full_title}",
            directive_map.get(risk_level, ""),
            "",
            f"**Category:** `{category}` | **Diet Fit:** `{'Compatible' if self.diet_type in food.get('diet_types', []) else 'Check Preference'}`",
            ""
        ]

        resp.append("**Clinical Verdict & Safety Analysis:**")
        for v in verdicts:
            resp.append(f"- {v}")

        resp.append("")
        resp.append("**Nutritional Snapshot (per 100g serving):**")
        cal = food.get('energy_kcal', '-')
        prot = food.get('protein_g', '-')
        carb = food.get('carbohydrates_g', '-')
        fib = food.get('dietary_fiber_g', '-')
        fat = food.get('fat_g', '-')
        gi_str = f" | **GI:** `{gi}`" if gi != "N/A" else ""
        resp.append(f"- **Energy:** `{cal} kcal` | **Protein:** `{prot}g` | **Fiber:** `{fib}g` | **Carbs:** `{carb}g` | **Fat:** `{fat}g`{gi_str}")
        resp.append(f"- **Sodium:** `{sod_mg} mg` | **Potassium:** `{pot_mg} mg` | **Calcium:** `{food.get('calcium_mg', '-')} mg`")

        benefit = food.get("health_benefit", "")
        if benefit:
            resp.append(f"\n💡 **Clinical Action:** *{benefit}*")

        return "\n".join(resp)

    # -------------------------------------------------------------------------
    # NUTRIENT-FOCUSED QUERY HANDLER
    # -------------------------------------------------------------------------
    def answer_nutrient_query(self, nutrient_key):
        ranked = filter_and_rank_foods(self.profile, active_profiles=self.active_profiles)

        nutrient_labels = {
            "protein": ("Protein-Rich Indian Foods", "protein_g", "g", True),
            "fiber": ("High-Fiber ICMR-NIN Foods", "dietary_fiber_g", "g", True),
            "low_sodium": ("Cardio & Renal Safe Low-Sodium Foods", "sodium_mg", "mg", False),
            "low_gi": ("Low Glycemic Index (<55) Foods for Blood Sugar", "glycemic_index", "", False)
        }

        title, key, unit, higher_is_better = nutrient_labels.get(nutrient_key, ("Nutritious Foods", "protein_g", "g", True))

        valid_items = []
        for f in ranked:
            if f.get("score", 0) < 0:
                continue
            val = f.get(key)
            if isinstance(val, (int, float)):
                valid_items.append(f)

        if higher_is_better:
            valid_items.sort(key=lambda x: x.get(key, 0) or 0, reverse=True)
        else:
            valid_items.sort(key=lambda x: x.get(key, 9999) or 9999)

        top_picks = valid_items[:5]

        resp = [
            f"### 🥗 Top {title}",
            f"Strictly filtered to match your **{self.diet_type}** preferences and exclude your declared allergens:",
            ""
        ]

        for idx, item in enumerate(top_picks, 1):
            name = item.get("name")
            local = item.get("local_name")
            full_n = f"{name} ({local})" if local else name
            val = item.get(key)
            cal = item.get("energy_kcal", "-")
            resp.append(f"**{idx}. {full_n}**")
            resp.append(f"- **{key.replace('_', ' ').title()}:** `{val} {unit}` | **Energy:** `{cal} kcal`")
            resp.append(f"- **Benefit:** {item.get('health_benefit', 'Nutrient-rich staple.')}")
            resp.append("")

        return "\n".join(resp)

    # -------------------------------------------------------------------------
    # ACTIVE MEDICATION & DRUG-FOOD INTERACTION AUDIT
    # -------------------------------------------------------------------------
    def answer_drug_interactions(self):
        if not self.active_profiles:
            return "You currently have no active prescriptions in the database that require specific drug-food precautions."

        resp = [
            f"### 💊 Active Medication Food & Administration Advisories",
            f"Clinical dietary rules for your **{len(self.active_profiles)} active prescription(s)**:",
            ""
        ]

        critical = self.analysis.get("critical_alerts", [])
        if critical:
            resp.append("**🚨 Critical Food Contraindications:**")
            for alert in critical:
                resp.append(f"- 🛑 **{alert['medicine']}:** {alert['alert']}")
            resp.append("")

        timings = self.analysis.get("meal_timing_guidance", [])
        if timings:
            resp.append("**🍽️ Meal & Dosing Timing Guidance:**")
            for t in timings:
                resp.append(f"- ⏰ **{t['medicine']}:** {t['timing']}")
            resp.append("")

        synergies = self.analysis.get("beneficial_items", [])
        if synergies:
            resp.append("**🌟 Evidence-Based Dietary Synergies:**")
            for s in synergies:
                resp.append(f"- ✨ {s}")
            resp.append("")

        resp.append("> ℹ️ *Always maintain consistent daily dosing times and notify your physician if you introduce major dietary changes.*")
        return "\n".join(resp)

    # -------------------------------------------------------------------------
    # COMORBIDITY GUIDANCE
    # -------------------------------------------------------------------------
    def answer_condition_guidance(self, condition):
        if condition == "DISEASE_DIABETES":
            return (
                "### 🩺 Evidence-Based Dietary Guidelines: Type 2 Diabetes\n"
                "- **Prioritize Low-GI Carbs (<55):** Finger millet (Ragi), Sorghum (Jowar), Pearl millet (Bajra), steel-cut oats, and legumes.\n"
                "- **Viscous Soluble Fiber:** Incorporate fenugreek (methi seeds/leaves), isabgol, and green leafy vegetables to blunt postprandial glucose surges.\n"
                "- **Eliminate High-GI Spikes:** Avoid refined flour (maida), white bakery breads, polished white rice in excess, and sugary fruit juices.\n"
                "- **Portion & Timing:** Distribute carbohydrate intake evenly across 3 regular meals; avoid large evening carbohydrate loads.\n"
                "- **Medication Note:** If on Metformin, take doses with meals to minimize gastrointestinal distress."
            )
        elif condition == "DISEASE_HYPERTENSION":
            return (
                "### 🩺 Evidence-Based Dietary Guidelines: Essential Hypertension (DASH Diet)\n"
                "- **Sodium Restriction:** Cap daily sodium intake below **2,000 mg** (approx. 1 level teaspoon of table salt).\n"
                "- **Potassium & Magnesium Enrichment:** Consume potassium-rich natural foods (leafy greens, garlic, cucumbers, and tender coconut water).\n"
                "- **Cardiovascular Synergies:** Garlic (Allicin) and amla (Vitamin C) enhance nitric oxide production and promote arterial vasodilation.\n"
                "- **Medication Note:** If taking **Amlodipine**, strictly avoid **Grapefruit / Pomelo** due to CYP3A4 inhibition."
            )
        elif condition == "DISEASE_CKD":
            return (
                "### 🩺 Evidence-Based Dietary Guidelines: Chronic Kidney Disease (CKD)\n"
                "- **Potassium Restriction:** Strictly avoid high-potassium foods (>250mg) such as coconut water, bananas, raw spinach, and citrus juices.\n"
                "- **Sodium Control:** Keep sodium below 1,500 mg/day to prevent fluid retention and peripheral edema.\n"
                "- **Protein Quality:** Prioritize high biological value proteins in measured quantities recommended by your nephrologist."
            )
        elif condition == "DISEASE_GOUT":
            return (
                "### 🩺 Evidence-Based Dietary Guidelines: Hyperuricemia & Gout\n"
                "- **Strict Purine Avoidance:** Eliminate red meat, organ meats (liver, kidney), sardines, mackerel, and shellfish.\n"
                "- **Alkalizing Foods:** Encourage cherries, amla, cucumbers, low-fat curd, and oats to promote renal uric acid clearance.\n"
                "- **Hydration:** Drink at least 2.5–3 liters of water daily to dilute serum urate."
            )
        else:
            return (
                "### 🩺 Personalized Health & Nutrition Overview\n"
                f"Your profile reflects: **{self.diet_type}** diet, with **{len(self.active_profiles)} active medication(s)**.\n"
                "Ask me about specific meal ideas (Breakfast, Lunch, Dinner, Snacks) or safety checks on any Indian food!"
            )

    # -------------------------------------------------------------------------
    # MAIN QUERY DISPATCHER
    # -------------------------------------------------------------------------
    def process_query(self, user_message, api_key=None, chat_history=None):
        """Processes any user message, using Gemini API if key is present, else local CDS."""
        if not user_message or not user_message.strip():
            return "Please type a question about food options, meal ideas, or medicine safety."

        # If a valid Gemini API key is provided, route through Gemini for open-ended dialogue
        if api_key and str(api_key).strip().startswith("AIza"):
            try:
                gemini_resp = call_gemini_api(api_key.strip(), user_message, self.profile, chat_history=chat_history)
                return gemini_resp
            except Exception as e:
                # If Gemini fails, gracefully proceed with local engine below
                pass

        # Otherwise, process with the 100% local Clinical Decision Support (CDS) Engine
        intent = self.classify_intent(user_message)

        if intent == "GREETING":
            name = self.profile.get("full_name", "there")
            diet = self.profile.get("diet_type", "Vegetarian")
            allergies_str = self.profile.get("allergies_raw", "None") or "None declared"
            comorbs = ", ".join(self.profile.get("comorbidity_names", [])) or "General Wellness"
            med_count = len(self.active_profiles)

            return (
                f"Hello **{name}**! 👋 I am your **MediAssist AI Clinical Dietary Assistant**.\n\n"
                f"I am actively monitoring your health profile:\n"
                f"- **Diet Type:** `{diet}` | **Allergens:** `{allergies_str}`\n"
                f"- **Diagnosed Conditions:** `{comorbs}`\n"
                f"- **Active Prescriptions:** `{med_count} Medication(s)`\n\n"
                "**Ask me anything about your diet & medicines!** For example:\n"
                "- 🍳 *'What breakfast is best for my diabetes & hypertension?'*\n"
                "- 🍲 *'Can I eat khichdi or idli for dinner?'*\n"
                "- 🥥 *'Can I drink coconut water with my blood pressure medicine?'*\n"
                "- 🔬 *'Why does grapefruit interact with my Amlodipine?'*\n"
                "- 🛑 *'Can I eat peanuts or peanut butter?'*\n"
                "- 🍵 *'Suggest high-protein snacks without peanuts.'*"
            )

        elif intent.startswith("PREPARED_DISH_"):
            dish_key = intent.replace("PREPARED_DISH_", "")
            return self.answer_prepared_dish(dish_key)

        elif intent.startswith("WHY_"):
            return self.answer_why_pharmacology(intent)

        elif intent.startswith("SYMPTOM_"):
            return self.answer_symptoms(intent)

        elif intent.startswith("COMPARE_"):
            return self.answer_comparison(intent)

        elif intent.startswith("LIFESTYLE_"):
            return self.answer_lifestyle(intent)

        elif intent == "MEAL_BREAKFAST":
            return self.recommend_meal("breakfast")
        elif intent == "MEAL_LUNCH":
            return self.recommend_meal("lunch")
        elif intent == "MEAL_DINNER":
            return self.recommend_meal("dinner")
        elif intent == "MEAL_SNACKS":
            return self.recommend_meal("snacks")
        elif intent == "MEAL_PLAN":
            return self.recommend_meal("lunch")

        elif intent == "DRUG_INTERACTIONS":
            return self.answer_drug_interactions()

        elif intent == "NUTRIENT_PROTEIN":
            return self.answer_nutrient_query("protein")
        elif intent == "NUTRIENT_FIBER":
            return self.answer_nutrient_query("fiber")
        elif intent == "NUTRIENT_LOW_SODIUM":
            return self.answer_nutrient_query("low_sodium")
        elif intent == "NUTRIENT_LOW_GI":
            return self.answer_nutrient_query("low_gi")

        elif intent.startswith("DISEASE_"):
            return self.answer_condition_guidance(intent)

        elif intent == "FOOD_SAFETY":
            matched_food = self.find_food_in_query(user_message)
            if matched_food:
                return self.evaluate_food_safety(matched_food)
            else:
                q_low = user_message.lower()
                for alg in self.allergies:
                    if alg in q_low:
                        return (
                            f"### 🛑 ALLERGEN WARNING: {alg.upper()}\n"
                            f"You have a declared medical allergy to **{alg.title()}**. "
                            f"Consuming this item or preparations containing it can trigger severe allergic reactions. **Please strictly avoid.**"
                        )
                return (
                    "### 🔍 Food Inquiry\n"
                    "I couldn't identify the exact Indian food item in your inquiry. "
                    "Try asking about a specific dish or ingredient (e.g. *'Can I eat ragi?'*, *'Is khichdi safe?'*, *'Can I have idli or dosa?'*, *'Is grapefruit safe with my medicine?'*)."
                )

        else:
            matched_food = self.find_food_in_query(user_message)
            if matched_food:
                return self.evaluate_food_safety(matched_food)

            return (
                "### 💬 Dietary Guidance\n"
                f"I am ready to assist with your **{self.diet_type}** nutrition plan. Try asking:\n\n"
                "- 🍳 *'Suggest a healthy breakfast plan'* (tailored to your comorbidities)\n"
                "- 🍲 *'Can I eat khichdi or idli?'* (composite Indian meals)\n"
                "- 🍌 *'Can I eat bananas with my medicine?'* (checks drug-nutrient interactions)\n"
                "- 🔬 *'Why can't I have grapefruit with Amlodipine?'* (pharmacological mechanisms)\n"
                "- 💡 *'What to eat for acidity or bloating?'* (digestive symptom advice)"
            )


# =============================================================================
# 3. STREAMLIT UI RENDERER
# =============================================================================

def render_dietary_chat_interface(user_id):
    """Renders the conversational AI Dietary Assistant in Streamlit with hybrid local/Gemini mode."""
    assistant = ClinicalDietaryAssistant(user_id)

    if "food_chat_messages" not in st.session_state:
        st.session_state.food_chat_messages = []
    if "gemini_api_key" not in st.session_state:
        # Check environment variable
        st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    p = assistant.profile
    allergies_display = p['allergies_raw'] if p['allergies_raw'] else "None declared"
    comorbs_display = " &bull; ".join(p.get("comorbidity_names", [])) or "None"
    meds_count = len(assistant.active_profiles)

    # 1. Clinical Context Header
    has_api_key = bool(st.session_state.gemini_api_key and st.session_state.gemini_api_key.startswith("AIza"))
    engine_badge = "<span class='badge-pill badge-green'>✨ Google Gemini AI Connected</span>" if has_api_key else "<span class='badge-pill badge-blue'>🛡️ Local Offline CDS Engine Active</span>"

    st.markdown(f"""
    <div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 16px; margin-bottom: 12px;'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 18px;'>🩺</span>
                <span style='font-weight: 700; font-size: 14px; color: #0f172a;'>Patient Context Active:</span>
                <span class='badge-pill badge-green'>{p['diet_type']}</span>
                <span class='badge-pill badge-slate'>Allergy: {allergies_display}</span>
                <span class='badge-pill badge-blue'>{meds_count} Active Meds</span>
            </div>
            <div>
                {engine_badge}
            </div>
        </div>
        <div style='font-size: 12px; color: #475569; margin-top: 6px;'>
            <b>Diagnosed Conditions:</b> {comorbs_display}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Optional Gemini API Key Drawer
    with st.expander("⚙️ AI Engine Settings: Local Offline vs. Google Gemini API (Free)", expanded=False):
        st.markdown(
            "MediAssist AI operates **100% offline and free** using its built-in ICMR-NIN Clinical Decision Support (CDS) engine. "
            "If you want **open-ended, human-like dialogue** for recipes, symptoms, and complex conversational follow-ups, you can optionally connect a free Google Gemini API key."
        )
        api_input = st.text_input(
            "Google Gemini API Key (starts with `AIza...`):",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="Paste your free Gemini API key here...",
            help="Get a free API key from Google AI Studio: https://aistudio.google.com/app/apikey"
        )
        if api_input != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = api_input
            st.success("API key updated successfully!")
            st.rerun()

        st.caption("🔒 *Privacy Note: Your key remains stored in your local session memory and is never shared.* [Get a Free Gemini API Key (Takes 1 min)](https://aistudio.google.com/app/apikey)")

    # 3. Quick Consultation Starter Chips
    st.caption("💡 **Quick Consultation Starters (Click to Ask):**")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        if st.button("🍳 Diabetic Breakfast Plan", use_container_width=True, key="qc_bf"):
            st.session_state.pending_food_prompt = "What breakfast options are best for my diabetes and high blood pressure?"
    with sc2:
        if st.button("🚫 Food-Drug Clashes", use_container_width=True, key="qc_ddi"):
            st.session_state.pending_food_prompt = "Are there any food interactions with my active prescriptions?"
    with sc3:
        if st.button("🍲 Can I Eat Khichdi?", use_container_width=True, key="qc_khichdi"):
            st.session_state.pending_food_prompt = "Can I eat khichdi for dinner with my diabetes?"
    with sc4:
        if st.button("🔬 Why Grapefruit Interacts?", use_container_width=True, key="qc_why_gf"):
            st.session_state.pending_food_prompt = "Why can't I eat grapefruit with Amlodipine and Atorvastatin?"

    prompt_to_handle = None
    if "pending_food_prompt" in st.session_state and st.session_state.pending_food_prompt:
        prompt_to_handle = st.session_state.pending_food_prompt
        st.session_state.pending_food_prompt = None

    # 4. Chat Message Display Container
    chat_container = st.container()

    with chat_container:
        if not st.session_state.food_chat_messages:
            welcome_msg = assistant.process_query("hello")
            with st.chat_message("assistant", avatar="🥗"):
                st.markdown(welcome_msg)
        else:
            for msg in st.session_state.food_chat_messages:
                avatar = "👤" if msg["role"] == "user" else "🥗"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

    # 5. Chat Input & Processing
    user_input = st.chat_input("Ask any dietary or medical food question (e.g., 'Can I eat khichdi?', 'Why avoid grapefruit?', 'Suggest snacks')...")

    if user_input:
        prompt_to_handle = user_input

    if prompt_to_handle:
        st.session_state.food_chat_messages.append({"role": "user", "content": prompt_to_handle})

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_to_handle)

        with st.chat_message("assistant", avatar="🥗"):
            response_text = assistant.process_query(
                prompt_to_handle,
                api_key=st.session_state.gemini_api_key,
                chat_history=st.session_state.food_chat_messages[:-1]
            )
            st.markdown(response_text)

        st.session_state.food_chat_messages.append({"role": "assistant", "content": response_text})
        st.rerun()

    # 6. Reset History Control
    if st.session_state.food_chat_messages:
        cc1, cc2, cc3 = st.columns([1, 1, 1])
        with cc3:
            if st.button("🗑️ Reset Chat History", use_container_width=True, key="btn_clear_chat"):
                st.session_state.food_chat_messages = []
                st.rerun()
