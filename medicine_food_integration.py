"""
Medicine & Food Dietary Integration Module
------------------------------------------
Connects prescribed medications with evidence-based dietary advisories,
drug-food contraindications, meal-timing rules, and therapeutic food synergies.
"""

import json
from pathlib import Path
from database import get_connection

DATA_DIR = Path(__file__).parent / "data"
MEDICINES_DATA_FILE = DATA_DIR / "medicines_data.json"

_MEDICINES_CATALOG = None

def load_medicines_catalog():
    """Loads and caches the curated medicines & food interaction database."""
    global _MEDICINES_CATALOG
    if _MEDICINES_CATALOG is not None:
        return _MEDICINES_CATALOG

    if MEDICINES_DATA_FILE.exists():
        try:
            with open(MEDICINES_DATA_FILE, "r", encoding="utf-8") as f:
                _MEDICINES_CATALOG = json.load(f)
                return _MEDICINES_CATALOG
        except Exception as e:
            print(f"Error loading medicines_data.json: {e}")
            _MEDICINES_CATALOG = []
            return _MEDICINES_CATALOG
    return []


def get_all_known_medicine_names():
    """Returns a sorted list of all medicine names and popular brands for selection."""
    catalog = load_medicines_catalog()
    options = []
    for med in catalog:
        options.append(med["name"])
        for brand in med.get("brand_names", []):
            options.append(f"{brand} ({med['name']})")
    return sorted(list(set(options)))


def match_medicine_profile(medicine_query):
    """
    Fuzzy/partial matching to find medication profile from user query or DB record.
    Matches generic names, aliases, and brand names (e.g. 'Metformin HCl', 'Dolo', 'Amlong').
    """
    if not medicine_query or not str(medicine_query).strip():
        return None

    query = str(medicine_query).lower().strip()
    catalog = load_medicines_catalog()

    # Exact or substring match in name or id
    for med in catalog:
        med_name = med["name"].lower()
        med_id = med["id"].lower()
        if med_id in query or med_name in query or query in med_name:
            return med

    # Substring match in brand names
    for med in catalog:
        for brand in med.get("brand_names", []):
            brand_lower = brand.lower()
            if brand_lower in query or query in brand_lower:
                return med

    # Word-level overlap
    query_words = set(query.replace("-", " ").replace("/", " ").split())
    for med in catalog:
        target_words = set(med["name"].lower().split())
        for brand in med.get("brand_names", []):
            target_words.update(brand.lower().split())
        if query_words.intersection(target_words):
            return med

    return None


def get_user_active_medicines(user_id):
    """Fetch active prescribed medicines for the user from the database."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, medicine_name, medicine_type, dosage, instructions, start_date, end_date
            FROM medicines
            WHERE user_id = ?
            ORDER BY medicine_name ASC
        """, (user_id,))
        return cursor.fetchall()


def analyze_user_food_drug_interactions(user_id):
    """
    Analyzes all active medications of a patient and returns:
    - active_profiles: list of matched clinical drug profiles
    - meal_timing_guidance: specific timing recommendations for each drug
    - critical_alerts: urgent contraindications (e.g. Grapefruit + Amlodipine/Atorvastatin)
    - foods_to_avoid: categorized list of foods/substances to avoid
    - beneficial_foods: foods that therapeutically synergize with their regimens
    """
    user_meds = get_user_active_medicines(user_id)
    active_profiles = []
    critical_alerts = []
    meal_timing_guidance = []
    avoid_items = set()
    caution_items = set()
    beneficial_items = set()

    for med in user_meds:
        med_name = med["medicine_name"]
        profile = match_medicine_profile(med_name)
        if profile:
            active_profiles.append({
                "db_name": med_name,
                "dosage": med["dosage"],
                "profile": profile
            })

            if profile.get("critical_alert"):
                critical_alerts.append({
                    "medicine": profile["name"],
                    "alert": profile["critical_alert"]
                })

            if profile.get("meal_timing"):
                meal_timing_guidance.append({
                    "medicine": profile["name"],
                    "timing": profile["meal_timing"]
                })

            interactions = profile.get("food_interactions", {})
            for item in interactions.get("avoid", []):
                avoid_items.add(f"**{profile['name']}**: {item}")
            for item in interactions.get("caution", []):
                caution_items.add(f"**{profile['name']}**: {item}")
            for item in interactions.get("beneficial", []):
                beneficial_items.add(f"**{profile['name']}**: {item}")

    return {
        "user_medications": user_meds,
        "active_profiles": active_profiles,
        "critical_alerts": critical_alerts,
        "meal_timing_guidance": meal_timing_guidance,
        "avoid_items": list(avoid_items),
        "caution_items": list(caution_items),
        "beneficial_items": list(beneficial_items)
    }


def evaluate_food_against_medications(food, active_profiles):
    """
    Evaluates an IFCT food item against patient's active medication profiles.
    Returns: list of interaction flags:
    { "level": "danger" | "warning" | "synergy", "title": str, "detail": str }
    """
    flags = []
    if not active_profiles:
        return flags

    food_name_lower = (food.get("name", "") + " " + food.get("local_name", "")).lower()
    food_category = food.get("category", "")
    attrs = food.get("health_attributes", [])

    for entry in active_profiles:
        profile = entry["profile"]
        med_id = profile["id"]
        med_name = profile["name"]

        # 1. Grapefruit / Pomelo Contraindication with Calcium Channel Blockers & Statins
        if med_id in ["amlodipine", "atorvastatin"]:
            if any(term in food_name_lower for term in ["grapefruit", "pomelo", "chakotra"]):
                flags.append({
                    "level": "danger",
                    "title": f"⚠️ Strict Contraindication with {med_name}",
                    "detail": f"Grapefruit compounds inhibit intestinal CYP3A4 metabolism, dangerously escalating {med_name} blood levels."
                })

        # 2. Levothyroxine / Ciprofloxacin: Chelation / Spacing with High Calcium Dairy
        if med_id in ["levothyroxine", "ciprofloxacin"]:
            if food_category == "Milk & Dairy Products" or "high_calcium" in attrs or any(t in food_name_lower for t in ["milk", "curd", "paneer", "cheese"]):
                flags.append({
                    "level": "warning",
                    "title": f"⏱️ 2-4 Hr Spacing Required ({med_name})",
                    "detail": f"Calcium chelates {med_name}, reducing oral absorption significantly. Keep at least 2 to 4 hours between this dairy food and your dose."
                })

        # 3. Levothyroxine with Soy Products
        if med_id == "levothyroxine":
            if any(t in food_name_lower for t in ["soy", "soya", "tofu"]):
                flags.append({
                    "level": "warning",
                    "title": f"⏱️ Space Away from Levothyroxine",
                    "detail": "Soy isoflavones interfere with thyroid hormone absorption in the intestine."
                })

        # 4. Metformin Therapeutic Synergies (Vitamin B12 & Soluble Fiber)
        if med_id == "metformin":
            if "diabetic_friendly" in attrs and ("high_fiber" in attrs or "low_gi" in attrs):
                flags.append({
                    "level": "synergy",
                    "title": f"🌟 Synergizes with Metformin",
                    "detail": "High-fiber / low-GI profile supports glycemic control and blunts postprandial glucose surges."
                })

        # 5. Warfarin / Vitamin K Consistency
        if med_id == "warfarin":
            if food_category == "Green Leafy Vegetables" or any(t in food_name_lower for t in ["spinach", "palak", "kale", "methi", "coriander"]):
                flags.append({
                    "level": "warning",
                    "title": "⚖️ Maintain Consistent Daily Portion (Warfarin)",
                    "detail": "Rich in Vitamin K. Maintain a steady daily intake; avoid sudden spikes or drastic drops to keep your INR stable."
                })

        # 6. Iron Absorption Synergies & Inhibitors
        if med_id == "ferrous_ascorbate":
            if any(t in food_name_lower for t in ["amla", "lemon", "guava", "orange"]):
                flags.append({
                    "level": "synergy",
                    "title": "🌟 Enhances Iron Absorption",
                    "detail": "High Vitamin C content dramatically boosts elemental iron absorption."
                })
            elif any(t in food_name_lower for t in ["tea", "coffee", "chai"]):
                flags.append({
                    "level": "warning",
                    "title": "⏱️ Do Not Take with Iron Tablet",
                    "detail": "Tannins and polyphenols in tea/coffee inhibit iron absorption by up to 75%."
                })

        # 7. Diuretic (Furosemide) Potassium Replenishment
        if med_id == "furosemide":
            if "hypertension_friendly" in attrs or any(t in food_name_lower for t in ["coconut water", "banana", "spinach"]):
                flags.append({
                    "level": "synergy",
                    "title": "🌟 Replenishes Electrolytes (Furosemide)",
                    "detail": "Helps naturally offset urinary potassium and magnesium depletion caused by loop diuretics."
                })

    # If there is a danger flag, filter out any synergy flags for this food to avoid confusion
    has_danger = any(f["level"] == "danger" for f in flags)
    if has_danger:
        flags = [f for f in flags if f["level"] != "synergy"]

    return flags
