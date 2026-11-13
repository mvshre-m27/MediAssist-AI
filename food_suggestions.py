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
    from dietary_chatbot import render_dietary_chat_interface
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>🥗 Personalized Indian Nutrition & AI Consultation</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>ICMR-NIN Indian Food Composition Tables (500+ Foods), Conversational Dietary Planning & Evidence-Based Drug-Nutrient Synergy</p>
    </div>
    """, unsafe_allow_html=True)

    tab_chat, tab_browse = st.tabs([
        "💬 AI Dietary Consultation Chatbot",
        "🥗 ICMR-NIN Food Explorer (500+ Foods)"
    ])

    with tab_chat:
        render_dietary_chat_interface(user_id)

    with tab_browse:
        profile = get_user_dietary_profile(user_id)
        analysis = mfi.analyze_user_food_drug_interactions(user_id)
        active_profiles = analysis["active_profiles"]

        # Section 1: User Profile Pill
        with st.container(border=True):
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.markdown(f"**Diet Type:** `{profile['diet_type']}`")
            with col_p2:
                allergies_display = profile['allergies_raw'] if profile['allergies_raw'] else "None declared"
                st.markdown(f"**Allergens:** `{allergies_display}`")
            with col_p3:
                restr_display = profile['restrictions_raw'] if profile['restrictions_raw'] else "General wellness"
                st.markdown(f"**Restrictions:** `{restr_display}`")

            # Comorbidities display
            comorb_names = profile.get("comorbidity_names", [])
            if comorb_names:
                st.markdown(f"**Diagnosed Conditions:** " + " &bull; ".join([f"`{c}`" for c in comorb_names]))

            # Multi-Condition Harmonization Callout if conflicting conditions exist
            comorb_set = set(profile.get("comorbidities", []))
            if "hypertension" in comorb_set and "ckd" in comorb_set:
                st.warning("⚠️ **Renal Safety Override Active (Hypertension + CKD):** High-potassium DASH foods (>250mg) capped to protect against hyperkalemia.")
            elif "diabetes" in comorb_set and "gout" in comorb_set:
                st.info("💡 **Harmonization Active (Diabetes + Gout):** Low-purine, low-GI foods prioritized.")

        # Section 2: Prescription Drug-Nutrient Advisories (If active medications exist)
        if active_profiles:
            with st.container(border=True):
                st.markdown(f"**💊 Active Medication Food & Nutrition Advisories ({len(active_profiles)} Prescriptions)**")

                # Critical alerts
                if analysis["critical_alerts"]:
                    for alert in analysis["critical_alerts"]:
                        st.error(f"⚠️ **{alert['medicine']}:** {alert['alert']}")

                # Meal timing guidance
                if analysis["meal_timing_guidance"]:
                    st.caption("🍽️ **Meal & Administration Timing:**")
                    t_cols = st.columns(min(len(analysis["meal_timing_guidance"]), 3))
                    for idx, guide in enumerate(analysis["meal_timing_guidance"]):
                        col_target = t_cols[idx % len(t_cols)]
                        with col_target:
                            st.markdown(f"&bull; **{guide['medicine']}:** *{guide['timing']}*")

                # Avoid vs Beneficial
                adv_col1, adv_col2 = st.columns(2)
                with adv_col1:
                    if analysis["avoid_items"]:
                        with st.expander("🚫 Foods/Substances to Space Out", expanded=False):
                            for item in analysis["avoid_items"]:
                                st.markdown(f"- {item}")
                with adv_col2:
                    if analysis["beneficial_items"]:
                        with st.expander("🌟 Beneficial Dietary Synergies", expanded=False):
                            for item in analysis["beneficial_items"]:
                                st.markdown(f"- {item}")

        # Section 3: Interactive Search, Category & Condition Controls
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.4, 1.2])

        with ctrl_col1:
            search_query = st.text_input("Search Food, Local Name, or Nutrient", placeholder="e.g. Ragi, Methi, Palak, Fiber...", label_visibility="collapsed")

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
            selected_category = st.selectbox("Category", categories, label_visibility="collapsed")

        with ctrl_col3:
            condition_options = {
                "All Recommended": None,
                "Hypertension (DASH)": "hypertension",
                "Diabetic (Low-GI)": "diabetes",
                "Heart-Healthy": "heart"
            }
            cond_choice = st.selectbox("Clinical Focus", list(condition_options.keys()), label_visibility="collapsed")
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
        st.caption(f"Showing **{total_matches}** verified authentic Indian foods matching your filters:")

        if not foods:
            st.warning("No foods matched your current search and allergen filters. Try adjusting your search query.")
        else:
            # Pagination controls
            page_size = 12
            total_pages = max(1, (total_matches + page_size - 1) // page_size)

            if total_pages > 1:
                pag_col1, pag_col2, pag_col3 = st.columns([1, 1.5, 1])
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
                            # Category Badge + Food Name
                            cat_name = food.get('category', '').upper()
                            st.markdown(
                                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>"
                                f"<span style='font-size: 15px; font-weight: 700; color: #0f172a;'>{food['name']}</span>"
                                f"<span class='badge-pill badge-green'>{cat_name}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                            # Drug interaction flags (if any)
                            for dflag in food.get("drug_flags", []):
                                if dflag["level"] == "danger":
                                    st.error(f"🛑 {dflag['title']}: {dflag['detail']}")
                                elif dflag["level"] == "warning":
                                    st.warning(f"⚠️ {dflag['title']}: {dflag['detail']}")
                                elif dflag["level"] == "synergy":
                                    st.success(f"🌟 {dflag['title']}: {dflag['detail']}")

                            # Key Metrics Badges
                            gi_val = food.get("glycemic_index", "N/A")
                            gi_pill = f"<span class='badge-pill badge-blue'>GI: {gi_val}</span>" if isinstance(gi_val, (int, float)) else ""
                            prot = food.get('protein_g', '-')
                            fib = food.get('dietary_fiber_g', '-')
                            kcal = food.get('energy_kcal', '-')

                            st.markdown(
                                f"<div style='display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0;'>"
                                f"{gi_pill}"
                                f"<span class='badge-pill badge-slate'>{kcal} kcal</span>"
                                f"<span class='badge-pill badge-slate'>Protein: {prot}g</span>"
                                f"<span class='badge-pill badge-slate'>Fiber: {fib}g</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                            st.markdown(f"**Health Action:** <span style='font-size: 13px; color: #334155;'>{food.get('health_benefit', 'Nutrient-rich staple.')}</span>", unsafe_allow_html=True)

                            # Nutrients expander
                            with st.expander("📊 Complete Nutritional Profile (per 100g)", expanded=False):
                                n_c1, n_c2 = st.columns(2)
                                with n_c1:
                                    st.markdown(f"&bull; Energy: `{food.get('energy_kcal', '-')} kcal`")
                                    st.markdown(f"&bull; Carbohydrates: `{food.get('carbohydrates_g', '-')} g`")
                                    st.markdown(f"&bull; Total Fat: `{food.get('fat_g', '-')} g`")
                                with n_c2:
                                    st.markdown(f"&bull; Potassium: `{food.get('potassium_mg', '-')} mg`")
                                    st.markdown(f"&bull; Sodium: `{food.get('sodium_mg', '-')} mg`")
                                    st.markdown(f"&bull; Calcium: `{food.get('calcium_mg', '-')} mg`")

                            # Algorithmic Rationale Box
                            st.markdown(
                                f"""
                                <div style='background-color: #f0fdf4; border-left: 3px solid #10b981; padding: 6px 10px; border-radius: 4px; margin-top: 6px; font-size: 12px; color: #166534;'>
                                    <b>Why Recommended:</b> {' &bull; '.join(food.get('reasons', []))}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
