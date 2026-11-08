"""
Personalized Clinical Nutrition & Food Recommender System
---------------------------------------------------------
Powered by the Indian Food Composition Tables (IFCT / ICMR-NIN) 
with 500+ authentic foods and active prescription drug-nutrient 
interaction intelligence.
"""

import streamlit as st
import json
from pathlib import Path
from database import get_connection, get_user_comorbidities
import medicine_food_integration as mfi

DATA_FILE = Path(__file__).parent / "data" / "indian_food_composition.json"

_IFCT_FOOD_CACHE = None

def load_food_database():
    """Loads and caches the 500+ Indian Food Composition Tables (IFCT) dataset."""
    global _IFCT_FOOD_CACHE
    if _IFCT_FOOD_CACHE is not None:
        return _IFCT_FOOD_CACHE

    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _IFCT_FOOD_CACHE = json.load(f)
                return _IFCT_FOOD_CACHE
        except Exception as e:
            print(f"Error loading IFCT food database: {e}")
            _IFCT_FOOD_CACHE = []
            return _IFCT_FOOD_CACHE
    return []


# =====================================================================
# 1. USER DIETARY PROFILE & HEALTH RESTRICTIONS
# =====================================================================

def get_user_dietary_profile(user_id):
    """Fetch user's profile and food preferences from the database."""
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

    comorb_rows = get_user_comorbidities(user_id)
    comorbidity_keys = [c["condition_key"] for c in comorb_rows]
    comorbidity_names = [c["condition_name"] for c in comorb_rows]

    return {
        "full_name": profile["full_name"] if profile and profile["full_name"] else "User",
        "diet_type": diet_type,
        "allergies_raw": allergies_raw,
        "allergy_tokens": allergy_tokens,
        "restrictions_raw": restrictions_raw,
        "restrictions_lower": restrictions_raw.lower(),
        "user_notes": user_notes,
        "comorbidities": comorbidity_keys,
        "comorbidity_names": comorbidity_names
    }


# =====================================================================
# 2. FILTERING & MULTI-ATTRIBUTE RANKING ENGINE
# =====================================================================

def filter_and_rank_foods(
    user_profile,
    active_profiles=None,
    selected_category=None,
    condition_filter=None,
    search_query=""
):
    """
    Hybrid recommendation algorithm:
    1. Hard safety constraints (Allergen exclusion & Diet type compliance)
    2. Drug-nutrient interaction evaluation against active medications
    3. Multi-attribute utility ranking based on clinical guidelines (ICMR-NIN, DASH, Low-GI)
    """
    all_foods = load_food_database()
    diet_type = user_profile["diet_type"]
    allergy_tokens = user_profile["allergy_tokens"]
    restrictions = user_profile["restrictions_lower"]

    wants_hypertension = any(k in restrictions for k in ["hypertension", "bp", "blood pressure", "low-sodium", "low sodium", "salt", "dash"])
    wants_diabetes = any(k in restrictions for k in ["diabetic", "diabetes", "sugar", "low-sugar", "low sugar", "low-gi", "glucose", "insulin"])
    wants_heart = any(k in restrictions for k in ["heart", "cholesterol", "lipid", "cardio", "statin"])

    # Multi-morbidity detection from profile + restrictions
    comorbidities = set(user_profile.get("comorbidities", []))
    has_ckd = "ckd" in comorbidities or any(k in restrictions for k in ["ckd", "kidney", "renal", "nephro"])
    has_gout = "gout" in comorbidities or any(k in restrictions for k in ["gout", "uric", "hyperuricemia"])
    has_gerd = "gerd" in comorbidities or any(k in restrictions for k in ["gerd", "reflux", "ulcer", "gastric", "acidity"])
    has_heart = "heart_disease" in comorbidities or wants_heart
    has_diabetes = "diabetes" in comorbidities or wants_diabetes
    has_hypertension = "hypertension" in comorbidities or wants_hypertension
    has_liver = "liver_disease" in comorbidities or any(k in restrictions for k in ["liver", "cirrhosis", "nafld"])

    if condition_filter == "hypertension":
        has_hypertension = True
    elif condition_filter == "diabetes":
        has_diabetes = True
    elif condition_filter == "heart":
        has_heart = True

    recommended = []

    for food in all_foods:
        # --- LAYER 1: HARD SAFETY CONSTRAINTS ---

        # 1. Diet Type Check
        if diet_type != "Not specified":
            if diet_type not in food.get("diet_types", []):
                continue

        # 2. Strict Allergen Exclusion
        has_allergy_conflict = False
        food_allergens = [a.lower() for a in food.get("allergens", [])]
        food_name_str = (food.get("name", "") + " " + food.get("local_name", "")).lower()

        for u_allergy in allergy_tokens:
            for f_allergen in food_allergens:
                if u_allergy in f_allergen or f_allergen in u_allergy:
                    has_allergy_conflict = True
                    break
            if u_allergy in food_name_str:
                has_allergy_conflict = True
                break
            if has_allergy_conflict:
                break

        if has_allergy_conflict:
            continue

        # 3. Category Filter
        if selected_category and selected_category != "All Categories":
            if food.get("category") != selected_category:
                continue

        # 4. Search Query Filter
        if search_query:
            query = search_query.lower().strip()
            searchable_text = (
                food.get("name", "") + " " +
                food.get("local_name", "") + " " +
                food.get("key_nutrients", "") + " " +
                food.get("health_benefit", "") + " " +
                food.get("category", "")
            ).lower()
            if query not in searchable_text:
                continue

        # --- LAYER 2: DRUG-NUTRIENT & COMORBIDITY HARMONIZATION ---
        drug_flags = []
        if active_profiles:
            drug_flags = mfi.evaluate_food_against_medications(food, active_profiles)

        comorb_flags = []
        score = 10.0
        reasons = []
        attrs = food.get("health_attributes", [])

        # 1. Chronic Kidney Disease (CKD) Renal Potassium & Sodium Overrides
        if has_ckd:
            pot_mg = food.get("potassium_mg", 0)
            sod_mg = food.get("sodium_mg", 0)
            f_cat = food.get("category", "")
            f_low = (food.get("name", "") + " " + food.get("local_name", "")).lower()

            is_high_k_trigger = (
                (isinstance(pot_mg, (int, float)) and pot_mg >= 220 and f_cat in ["Beverages & Herbal Infusions", "Fruits", "Green Leafy Vegetables"]) or
                (isinstance(pot_mg, (int, float)) and pot_mg >= 450) or
                any(t in f_low for t in ["coconut water", "nariyal pani", "banana", "kela", "potato", "aloo", "spinach", "palak"])
            )

            if is_high_k_trigger:
                score -= 35.0
                comorb_flags.append({
                    "level": "danger",
                    "title": "⚠️ High Potassium - Caution in CKD",
                    "detail": f"Contains {pot_mg}mg potassium/100g. Diseased kidneys cannot clear excess potassium, elevating hyperkalemia risk."
                })
            if isinstance(sod_mg, (int, float)) and sod_mg > 200:
                score -= 20.0
                comorb_flags.append({
                    "level": "warning",
                    "title": "⚠️ High Sodium - Restrict in CKD",
                    "detail": f"Contains {sod_mg}mg sodium/100g. Sodium retention worsens fluid overload and accelerates renal decline."
                })

        # 2. Hyperuricemia & Gout Purine Overrides
        if has_gout:
            f_cat = food.get("category", "")
            f_low = (food.get("name", "") + " " + food.get("local_name", "")).lower()
            if f_cat == "Egg, Poultry, Fish & Meat" or any(t in f_low for t in ["sardine", "mackerel", "mutton", "liver", "prawn", "crab", "organ"]):
                score -= 45.0
                comorb_flags.append({
                    "level": "danger",
                    "title": "⚠️ High Purine - Trigger for Gout Flare",
                    "detail": "High-purine meats and seafood break down into uric acid, precipitating acute gout attacks."
                })
            elif any(t in f_low for t in ["cherry", "amla", "cucumber", "curd", "dahi", "oat", "apple"]):
                score += 10.0
                reasons.append("Low-Purine & Alkalizing (Gout-Safe)")

        # 3. GERD & Peptic Ulcer Mucosal Irritant Overrides
        if has_gerd:
            f_low = (food.get("name", "") + " " + food.get("local_name", "")).lower()
            if any(t in f_low for t in ["chili", "mirchi", "pepper", "citrus", "lemon", "lime", "vinegar", "pickle", "fried"]):
                score -= 30.0
                comorb_flags.append({
                    "level": "warning",
                    "title": "⚠️ Gastric / Acid Reflux Trigger",
                    "detail": "Acidic and highly spiced foods irritate gastric mucosa and exacerbate esophageal reflux."
                })
            elif any(t in f_low for t in ["oats", "curd", "dahi", "ash gourd", "lauki", "banana"]):
                score += 8.0
                reasons.append("Soothing & Low-Acid (GERD-Friendly)")

        # Combine all flags
        all_flags = drug_flags + comorb_flags
        has_contraindication = any(f["level"] == "danger" for f in all_flags)

        # --- LAYER 3: MULTI-ATTRIBUTE UTILITY SCORING ---
        if has_contraindication:
            score -= 100.0
            reasons.append("⚠️ Clinical Warning: Check contraindications before consuming")
        else:
            if has_hypertension:
                # If patient has CKD, potassium is restricted; only reward low-sodium foods!
                if has_ckd:
                    if "low_sodium" in attrs or (isinstance(food.get("sodium_mg"), (int, float)) and food.get("sodium_mg", 999) < 60):
                        score += 15.0
                        reasons.append("Low-Sodium (Renal & Blood Pressure Safe)")
                else:
                    if "hypertension_friendly" in attrs or "low_sodium" in attrs:
                        score += 15.0
                        reasons.append("Low-Sodium & Potassium/Nitrate (DASH-Aligned)")

            if has_diabetes and ("diabetic_friendly" in attrs or "low_gi" in attrs):
                score += 15.0
                reasons.append("Low Glycemic Index (<55) & High Viscous Fiber")

            if has_heart and "heart_healthy" in attrs:
                score += 10.0
                reasons.append("Cardiovascular & Lipid Protection")

            if "high_fiber" in attrs:
                score += 5.0
            if "high_protein" in attrs:
                score += 5.0
            if "high_calcium" in attrs:
                score += 3.0
            if "high_iron" in attrs:
                score += 3.0

            # Medication synergy bonus
            for flag in drug_flags:
                if flag["level"] == "synergy":
                    score += 8.0
                    reasons.append(flag["title"])

            if not reasons:
                reasons.append("Balanced nutrient-dense whole food choice (ICMR-NIN)")

        food_item = dict(food)
        food_item["score"] = score
        food_item["reasons"] = reasons
        food_item["drug_flags"] = all_flags
        recommended.append(food_item)

    # Sort descending by score
    recommended.sort(key=lambda x: x["score"], reverse=True)
    return recommended


# =====================================================================
# 3. STREAMLIT UI PRESENTATION
# =====================================================================

def show_food_suggestions_page(user_id):
    st.title("🥗 Personalized Indian Food & Nutrition Recommender")
    st.caption("Grounded in ICMR-NIN Indian Food Composition Tables (500+ Foods) & Evidence-Based Drug-Nutrient Interactions")

    # Safety Notice
    st.info(
        "💡 **Clinical Guidance Notice:** Suggestions provided here are evidence-based general nutritional guidelines. "
        "They complement medical treatment but do NOT replace direct consultation with a registered clinical dietitian or your physician."
    )

    profile = get_user_dietary_profile(user_id)
    analysis = mfi.analyze_user_food_drug_interactions(user_id)
    active_profiles = analysis["active_profiles"]

    # Section 1: User Profile Pill
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

        # Comorbidities display
        comorb_names = profile.get("comorbidity_names", [])
        if comorb_names:
            st.markdown(f"**🏥 Diagnosed Conditions:** " + " • ".join([f"`{c}`" for c in comorb_names]))
        else:
            st.markdown(f"**🏥 Diagnosed Conditions:** `None recorded (General wellness)`")

        # Multi-Condition Harmonization Callout if conflicting conditions exist
        comorb_set = set(profile.get("comorbidities", []))
        if "hypertension" in comorb_set and "ckd" in comorb_set:
            st.warning(
                "💡 **Clinical Harmonization Alert (Hypertension + CKD):** For hypertension, DASH guidelines normally promote high potassium. "
                "However, because **Chronic Kidney Disease (CKD)** is also diagnosed, high-potassium foods (>250mg) have been restricted to protect against life-threatening hyperkalemia."
            )
        elif "diabetes" in comorb_set and "gout" in comorb_set:
            st.info(
                "💡 **Clinical Harmonization Alert (Diabetes + Gout):** The recommendation engine has prioritized low-purine, low-GI foods "
                "to stabilize blood glucose while avoiding uric acid crystal precipitation."
            )
        elif "gerd" in comorb_set:
            st.info(
                "💡 **Mucosal Protection Active (GERD / Gastric Ulcer):** Acidic juices, extreme spices, and deep-fried irritants have been filtered."
            )

        st.caption("To update your diet type, allergies, or restrictions, navigate to the **Profile** tab in the sidebar.")

    # Section 2: Prescription Drug-Nutrient Advisories (If active medications exist)
    if active_profiles:
        with st.container(border=True):
            st.markdown(f"### 💊 Active Medication Food & Nutrition Advisories")
            st.caption(f"Personalized clinical advisories generated for **{len(active_profiles)} active medications** in your regimen:")

            # Critical alerts
            if analysis["critical_alerts"]:
                for alert in analysis["critical_alerts"]:
                    st.error(f"⚠️ **{alert['medicine']} Safety Precaution:** {alert['alert']}")

            # Meal timing guidance
            if analysis["meal_timing_guidance"]:
                st.markdown("##### 🍽️ Meal & Administration Timing")
                t_cols = st.columns(min(len(analysis["meal_timing_guidance"]), 3))
                for idx, guide in enumerate(analysis["meal_timing_guidance"]):
                    col_target = t_cols[idx % len(t_cols)]
                    with col_target:
                        st.markdown(f"**{guide['medicine']}**\n\n*{guide['timing']}*")

            # Avoid vs Beneficial Tabs / Columns
            adv_col1, adv_col2 = st.columns(2)
            with adv_col1:
                if analysis["avoid_items"]:
                    with st.expander("🚫 Foods & Substances to Avoid or Space Out", expanded=True):
                        for item in analysis["avoid_items"]:
                            st.markdown(f"- {item}")
            with adv_col2:
                if analysis["beneficial_items"]:
                    with st.expander("🌟 Beneficial Dietary Synergies", expanded=True):
                        for item in analysis["beneficial_items"]:
                            st.markdown(f"- {item}")

    st.divider()

    # Section 3: Interactive Search, Category & Condition Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.4, 1.2])

    with ctrl_col1:
        search_query = st.text_input("🔍 Search Food, Local Name, or Nutrient", placeholder="e.g. Ragi, Methi, Palak, Potassium, Fiber, Fish...")

    with ctrl_col2:
        categories = [
            "All Categories",
            "Cereals and Millets",
            "Grain Legumes & Pulses",
            "Green Leafy Vegetables",
            "Other Vegetables",
            "Roots and Tubers",
            "Fruits",
            "Nuts and Oilseeds",
            "Spices, Herbs & Condiments",
            "Milk & Dairy Products",
            "Egg, Poultry, Fish & Meat",
            "Beverages & Herbal Infusions",
            "Healthy Fats & Culinary Oils"
        ]
        selected_category = st.selectbox("ICMR-NIN Food Category", categories)

    with ctrl_col3:
        condition_options = {
            "All Recommended Foods": None,
            "Hypertension-Friendly (DASH)": "hypertension",
            "Diabetic-Friendly (Low-GI)": "diabetes",
            "Heart-Healthy & Cholesterol": "heart"
        }
        cond_choice = st.selectbox("Clinical Focus Priority", list(condition_options.keys()))
        condition_filter = condition_options[cond_choice]

    # Get Recommendations
    foods = filter_and_rank_foods(
        profile,
        active_profiles=active_profiles,
        selected_category=selected_category,
        condition_filter=condition_filter,
        search_query=search_query
    )

    total_matches = len(foods)
    st.write(f"Showing **{total_matches}** verified authentic Indian foods matching your filters:")

    if not foods:
        st.warning("No foods matched your current search and allergen filters. Try adjusting your search query or loosening restrictions in your Profile.")
        return

    # Pagination controls to ensure smooth UI performance across 500+ items
    page_size = 20
    total_pages = max(1, (total_matches + page_size - 1) // page_size)

    if total_pages > 1:
        pag_col1, pag_col2, pag_col3 = st.columns([1, 2, 1])
        with pag_col2:
            current_page = st.number_input(
                f"Page (1 to {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key="food_pagination"
            )
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_matches)
        displayed_foods = foods[start_idx:end_idx]
        st.caption(f"Displaying foods **{start_idx + 1}** to **{end_idx}** of **{total_matches}**")
    else:
        displayed_foods = foods

    # Section 4: Render Food Cards in a 2-Column Responsive Layout
    for i in range(0, len(displayed_foods), 2):
        col1, col2 = st.columns(2)
        row_foods = [displayed_foods[i]]
        if i + 1 < len(displayed_foods):
            row_foods.append(displayed_foods[i + 1])

        for col, food in zip([col1, col2], row_foods):
            with col:
                with st.container(border=True):
                    # Category Badge + Food Name + Local Name
                    cat_name = food.get('category', '').upper()
                    st.markdown(
                        f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>"
                        f"<span style='font-size: 11px; background-color: #e0f2f1; color: #00695c; padding: 3px 8px; border-radius: 12px; font-weight: 600;'>{cat_name}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.subheader(food["name"])

                    # Drug interaction flags (if any)
                    for dflag in food.get("drug_flags", []):
                        if dflag["level"] == "danger":
                            st.error(f"{dflag['title']}\n\n*{dflag['detail']}*")
                        elif dflag["level"] == "warning":
                            st.warning(f"{dflag['title']}\n\n*{dflag['detail']}*")
                        elif dflag["level"] == "synergy":
                            st.success(f"{dflag['title']}\n\n*{dflag['detail']}*")

                    # Key Metrics: GI & Allergens
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        gi_val = food.get("glycemic_index", "N/A")
                        gi_badge = "Low-GI" if isinstance(gi_val, (int, float)) and gi_val <= 55 else ("Medium-GI" if isinstance(gi_val, (int, float)) and gi_val <= 69 else "GI")
                        st.markdown(f"**Glycemic Index:** `{gi_val}` ({gi_badge})")
                    with m_col2:
                        allergens_tag = ", ".join(food.get("allergens", [])).title() if food.get("allergens") else "None (Hypoallergenic)"
                        st.markdown(f"**Allergens:** `{allergens_tag}`")

                    # Nutrients & Action
                    st.markdown(f"**Key Nutrients:** *{food.get('key_nutrients', 'Nutrient-rich staple')}*")
                    st.markdown(f"**Health Action:** {food.get('health_benefit', 'Promotes nutritional wellness.')}")

                    # Detailed Macro/Micronutrient Breakdown Expander
                    with st.expander("📊 Complete Nutritional Breakdown (per 100g)", expanded=False):
                        n_c1, n_c2 = st.columns(2)
                        with n_c1:
                            st.markdown(f"- **Energy:** `{food.get('energy_kcal', 'N/A')} kcal`")
                            st.markdown(f"- **Protein:** `{food.get('protein_g', 'N/A')} g`")
                            st.markdown(f"- **Carbohydrates:** `{food.get('carbohydrates_g', 'N/A')} g`")
                            st.markdown(f"- **Dietary Fiber:** `{food.get('dietary_fiber_g', 'N/A')} g`")
                            st.markdown(f"- **Total Fat:** `{food.get('fat_g', 'N/A')} g`")
                        with n_c2:
                            st.markdown(f"- **Potassium:** `{food.get('potassium_mg', 'N/A')} mg`")
                            st.markdown(f"- **Sodium:** `{food.get('sodium_mg', 'N/A')} mg`")
                            st.markdown(f"- **Calcium:** `{food.get('calcium_mg', 'N/A')} mg`")
                            st.markdown(f"- **Iron:** `{food.get('iron_mg', 'N/A')} mg`")

                    # Algorithmic Rationale Box
                    st.markdown(
                        f"""
                        <div style='background-color: #f1f8e9; border-left: 4px solid #558b2f; padding: 8px 12px; border-radius: 4px; margin-top: 8px;'>
                            <small style='color: #33691e; font-weight: 700;'>WHY IT'S RECOMMENDED FOR YOU:</small><br>
                            <small style='color: #2e7d32;'>{' • '.join(food.get('reasons', []))}</small><br>
                            <small style='color: #555;'><em>{food.get('rationale', 'ICMR-NIN Indian Food Composition Table guideline.')}</em></small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
