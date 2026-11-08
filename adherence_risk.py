import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection, get_user_comorbidities
from adherence_history import get_adherence_data, calculate_adherence
import sys
from pathlib import Path

# Ensure ml directory is on sys.path
ML_DIR = Path(__file__).resolve().parent / "ml"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from predict_risk import (
    predict_adherence_risk,
    simulate_counterfactual,
    save_assessment_to_db,
    get_latest_user_assessment
)


def get_user_regimen_summary(user_id):
    """
    Fetch user's profile and active medication stats to auto-populate assessment.
    """
    with get_connection() as conn:
        profile = conn.execute("""
            SELECT full_name, age
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        medicines = conn.execute("""
            SELECT id, medicine_name, total_stock, remaining_stock
            FROM medicines
            WHERE user_id = ? AND is_active = 1
        """, (user_id,)).fetchall()

        # Count total dose schedules per day
        schedules = conn.execute("""
            SELECT COUNT(ds.id) as daily_doses
            FROM dose_schedules ds
            JOIN medicines m ON ds.medicine_id = m.id
            WHERE m.user_id = ? AND m.is_active = 1
        """, (user_id,)).fetchone()

    age = profile["age"] if profile and profile["age"] else 55
    name = profile["full_name"] if profile and profile["full_name"] else "User"
    med_count = len(medicines)
    daily_doses = schedules["daily_doses"] if schedules and schedules["daily_doses"] else 0
    estimated_units = max(daily_doses * 30, 30) if daily_doses > 0 else 60

    comorbs = get_user_comorbidities(user_id)
    comorb_keys = [c["condition_key"] for c in comorbs]
    comorb_names = [c["condition_name"] for c in comorbs]

    return {
        "name": name,
        "age": age,
        "med_count": med_count,
        "daily_doses": daily_doses,
        "estimated_units": estimated_units,
        "comorbidities": comorb_keys,
        "comorbidity_names": comorb_names
    }


def get_all_user_assessments(user_id):
    """Fetch assessment history for the user."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, risk_level, risk_score, model_version, assessed_at
            FROM adherence_assessments
            WHERE user_id = ?
            ORDER BY assessed_at DESC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


def show_adherence_risk_page(user_id):
    st.title("🎯 Medication Adherence Risk Assessment")
    st.caption("Explainable AI (XAI) & Random Forest Pipeline (ROC-AUC: 0.9006, Mendeley Adherence Cohort, 24,084 Patients)")

    # Medical & Prototype Disclaimer
    st.warning(
        "ℹ️ **Clinical & Prototype Notice:** This adherence risk assessment is an educational decision-support tool. "
        "It provides statistical probability estimates based on patient and regimen characteristics. It does NOT constitute a medical diagnosis "
        "or replace clinical judgment."
    )

    regimen = get_user_regimen_summary(user_id)

    # 1. Quick Stats from App Records
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Active Medicines", f"{regimen['med_count']}")
    with col_b:
        st.metric("Daily Doses Scheduled", f"{regimen['daily_doses']} doses/day")
    with col_c:
        past_records = get_adherence_data(user_id, days=15)
        if past_records:
            total, taken, missed, unconfirmed, adherence = calculate_adherence(past_records)
            if (taken + missed) > 0:
                st.metric("Recent 15-Day Adherence", f"{adherence:.1f}%")
            else:
                st.metric("Recent 15-Day Adherence", "Pending Confirmation")
        else:
            st.metric("Recent 15-Day Adherence", "N/A (No dose logs)")

    st.divider()

    # 2. Assessment Form
    st.subheader("📋 Patient Regimen & Clinical Profile")
    st.write("Review or adjust your profile metrics below to calculate non-adherence risk:")

    with st.form("adherence_ml_form"):
        col1, col2 = st.columns(2)

        with col1:
            patient_age = st.number_input(
                "Patient Age",
                min_value=16,
                max_value=110,
                value=int(regimen["age"]),
                step=1,
                help="Age is a significant factor in regimen complexity and cognitive routine maintenance."
            )

            # Intelligent clinical defaults from user's recorded comorbidities
            comorbs = set(regimen.get("comorbidities", []))
            if "hypertension" in comorbs and "diabetes" in comorbs:
                cond_idx = 2
            elif "diabetes" in comorbs:
                cond_idx = 1
            else:
                cond_idx = 0

            has_other_comorb = any(c in comorbs for c in ["ckd", "heart_disease", "gout", "gerd", "asthma", "liver_disease", "dyslipidemia", "osteoporosis"])
            comorb_idx = 1 if has_other_comorb or len(comorbs) >= 2 else 0

            primary_condition = st.selectbox(
                "Primary Chronic Condition",
                ["Hypertension (High Blood Pressure)", "Type 2 Diabetes", "Both Hypertension & Diabetes"],
                index=cond_idx,
                help="Mendeley research shows adherence dynamics differ between asymptomatic conditions (Hypertension) and symptomatic meal-linked conditions (Diabetes)."
            )

            comorbidity_status = st.selectbox(
                "Other Chronic Comorbidities?",
                ["No additional chronic comorbidities", "Yes, has other comorbidities (Cardiovascular, Kidney, etc.)"],
                index=comorb_idx
            )

        with col2:
            units_dispensed = st.number_input(
                "Estimated Monthly Medication Units (Pills/Injections)",
                min_value=10,
                max_value=300,
                value=int(regimen["estimated_units"]),
                step=5,
                help="Total unit burden dispensed in a 30-day refill cycle."
            )

            complications = st.selectbox(
                "History of Disease Complications?",
                ["No secondary complications", "Yes, history of complications"]
            )

            coverage_tier = st.selectbox(
                "Healthcare Scheme Coverage Tier",
                ["Standard Plan", "Medium Tier", "Premium / Comprehensive Tier"]
            )

        submitted = st.form_submit_button("⚡ Run ML Risk Assessment", use_container_width=True)

    if submitted:
        # Feature Mapping
        diagnosis_hyp = 1 if "Hypertension" in primary_condition else 0
        no_comorbidity = 1 if "No additional" in comorbidity_status else 0
        no_complication = 1 if "No secondary" in complications else 0

        scheme_medium = 1 if "Medium" in coverage_tier else 0
        scheme_premium = 1 if "Premium" in coverage_tier else 0
        cover_standard = 1 if "Standard" in coverage_tier else 0

        feature_dict = {
            "age": patient_age,
            "units_total": units_dispensed,
            "diagnosis_hypertension": diagnosis_hyp,
            "no_comorbidity": no_comorbidity,
            "no_complication": no_complication,
            "scheme_medium": scheme_medium,
            "scheme_premium": scheme_premium,
            "cover_standard": cover_standard,
            "annual_contribution": 690384.0 if not scheme_premium else 6889900.0,
            "annual_claim_amount": 25000.0 if no_complication == 1 else 85000.0,
            "gender_m": 1
        }

        with st.spinner("Analyzing regimen complexity and adherence patterns..."):
            result = predict_adherence_risk(feature_dict)
            feature_dict["_computed_prob"] = result["non_adherence_probability"]

            # Persist to SQLite
            assessment_id = save_assessment_to_db(
                user_id=user_id,
                risk_level=result["risk_level"],
                risk_score=result["non_adherence_probability"]
            )

            # Store in session state for interactive counterfactuals
            st.session_state["adherence_assessment_result"] = result
            st.session_state["adherence_assessment_features"] = feature_dict
            st.session_state["adherence_assessment_id"] = assessment_id

    # 3. Display Assessment Results & Explainable AI (XAI)
    if "adherence_assessment_result" in st.session_state:
        result = st.session_state["adherence_assessment_result"]
        base_features = st.session_state["adherence_assessment_features"]
        assessment_id = st.session_state.get("adherence_assessment_id")

        if assessment_id:
            st.success(f"Assessment complete! Logged as Assessment #{assessment_id}")

        st.markdown("### 📊 Assessment Findings & Risk Stratification")

        res_col1, res_col2 = st.columns([1, 1])

        with res_col1:
            st.markdown(
                f"""
                <div style="background-color: white; border: 2px solid {result['risk_color']}; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                    <div style="font-size: 13px; color: #666; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Predicted Adherence Status</div>
                    <div style="font-size: 34px; font-weight: 800; color: {result['risk_color']}; margin: 8px 0;">
                        {result['risk_label']}
                    </div>
                    <div style="font-size: 16px; color: #333; margin-bottom: 6px;">
                        Non-Adherence Risk Probability: <b>{result['non_adherence_probability']}%</b>
                    </div>
                    <div style="font-size: 14px; color: #2e7d32; font-weight: 600;">
                        Estimated Adherence Likelihood: <b>{result['adherence_probability']}%</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with res_col2:
            cohort = result["cohort_stats"]
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 12px; padding: 22px;">
                    <div style="font-size: 13px; color: #495057; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">👥 Cohort Population Benchmark</div>
                    <div style="font-size: 20px; font-weight: 700; color: #0d6efd; margin: 8px 0;">
                        Top {cohort['adherence_standing_pct']}% Adherence Standing
                    </div>
                    <div style="font-size: 13px; color: #555; line-height: 1.5;">
                        Compared against <b>24,084 chronic patients</b> in the multi-center clinical cohort:
                    </div>
                    <ul style="font-size: 13px; color: #444; margin-top: 6px; padding-left: 18px;">
                        <li>Patient Non-Adherence Risk: <b>{result['non_adherence_probability']}%</b></li>
                        <li>Cohort Median Risk: <b>{cohort['cohort_median']}%</b> | Cohort Mean: <b>{cohort['cohort_mean']}%</b></li>
                        <li><b>Outperforms {cohort['adherence_standing_pct']}%</b> of cohort patients in routine adherence stability.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # 4. Explainable AI: Directional Local Feature Attribution Breakdown
        st.subheader("🔬 Explainable AI: Factor Attribution & Risk Impact Breakdown")
        st.caption(
            "Mathematical and clinical decomposition of why the Random Forest model assigned this probability. "
            "Directional impacts reflect changes relative to population reference baselines."
        )

        protect_col, risk_col = st.columns(2)
        protect_factors = [f for f in result["factor_attributions"] if f["direction"] == "protective"]
        risk_factors = [f for f in result["factor_attributions"] if f["direction"] == "risk_factor"]

        with protect_col:
            st.markdown("#### 🟢 Protective Factors (Sustaining Adherence)")
            if protect_factors:
                for item in protect_factors:
                    st.markdown(
                        f"""
                        <div style="background-color: #f1f8e9; border-left: 4px solid #43a047; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 700; color: #2e7d32; font-size: 14px;">{item['feature']}</span>
                                <span style="background-color: #c8e6c9; color: #1b5e20; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 12px;">
                                    {item['delta_label']}
                                </span>
                            </div>
                            <div style="font-size: 12px; color: #555; margin-top: 4px;"><b>Metric:</b> {item['metric']}</div>
                            <div style="font-size: 12px; color: #333; margin-top: 6px; line-height: 1.4;">{item['rationale']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No dominant protective factors identified in current profile.")

        with risk_col:
            st.markdown("#### 🔴 Risk Escalators (Vulnerability Factors)")
            if risk_factors:
                for item in risk_factors:
                    st.markdown(
                        f"""
                        <div style="background-color: #fbe9e7; border-left: 4px solid #e53935; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 700; color: #c62828; font-size: 14px;">{item['feature']}</span>
                                <span style="background-color: #ffcdd2; color: #b71c1c; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 12px;">
                                    {item['delta_label']}
                                </span>
                            </div>
                            <div style="font-size: 12px; color: #555; margin-top: 4px;"><b>Metric:</b> {item['metric']}</div>
                            <div style="font-size: 12px; color: #333; margin-top: 6px; line-height: 1.4;">{item['rationale']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.success("No critical risk escalators detected! The patient's regimen exhibits stable low-friction characteristics.")

        # Multi-Morbidity Clinical Regimen Context
        c_names = regimen.get("comorbidity_names", [])
        if c_names:
            st.info(
                f"🩺 **Multi-Condition Complexity Context:** Managing **{len(c_names)} diagnosed chronic conditions** ({', '.join(c_names)}). "
                "Co-occurring conditions divide cognitive attention, multiply daily doses, and necessitate coordinated refill management."
            )

        st.divider()

        # 5. Global Model Feature Importance (Model Transparency)
        with st.expander("🌐 Global Model Transparency: How the Random Forest Algorithm Weighs Factors", expanded=False):
            st.write(
                "Trained across 24,084 chronic patients, the Random Forest model evaluates nonlinear interactions across "
                "regimen volume, clinical history, and demographic features. Here are the model's global feature weights:"
            )

            imp_df = pd.DataFrame(result["global_feature_importances"])
            imp_df = imp_df.rename(columns={
                "feature": "Clinical Dimension",
                "importance": "Global Weight (%)",
                "clinical_role": "Clinical Rationale"
            })
            st.dataframe(imp_df, use_container_width=True, hide_index=True)

            st.caption(
                "📌 **Clinical Note:** Medication Refill Volume (UNITSTOTAL, 55.2%) and Healthcare Claims (30.9%) "
                "constitute over 86% of total predictive power. In epidemiological research, active prescription refills "
                "are the single most reliable objective surrogate for true medication possession."
            )

        st.divider()

        # 6. Interactive "What-If" Counterfactual Sensitivity Simulator
        st.subheader("🧪 Interactive Counterfactual Sensitivity Simulator ('What-If' Analysis)")
        st.caption("Simulate how hypothetical shifts in medication supply, complications, or disease management would alter the predicted non-adherence risk:")

        sim_option = st.radio(
            "Select a Counterfactual Scenario to Test:",
            [
                "Baseline (Current Profile)",
                "Scenario A: Prescription Refill Lapse (Units drop by 75% due to pharmacy delay)",
                "Scenario B: Disease Complication Shock (Development of secondary clinical complications)",
                "Scenario C: Single-Condition Regimen (Elimination of polypharmacy friction)",
                "Scenario D: Meal-Anchored Diabetes Only (Blood glucose timing feedback)"
            ],
            index=0,
            horizontal=False
        )

        modifications = {}
        scenario_description = ""

        if "Scenario A" in sim_option:
            # Drop monthly units to 15 pills/month
            modifications = {"units_total": 15}
            scenario_description = "Refill lapse simulated: Prescription refill volume drops from regular refills to 15 pills/month (e.g. prescription abandonment or missed pickup)."
        elif "Scenario B" in sim_option:
            # Complications present
            modifications = {"no_complication": 0}
            scenario_description = "Complication emergence simulated: Patient develops secondary microvascular/cardiovascular complications that impair daily self-care stamina."
        elif "Scenario C" in sim_option:
            # No comorbidity
            modifications = {"no_comorbidity": 1}
            scenario_description = "Regimen simplification simulated: Multi-morbidity friction is eliminated; patient manages a single consolidated chronic regimen."
        elif "Scenario D" in sim_option:
            # Diabetes only (hypertension = 0)
            modifications = {"diagnosis_hypertension": 0}
            scenario_description = "Condition anchor simulated: Medication regimen shifts from asymptomatic hypertension to meal-anchored Type 2 Diabetes."

        if modifications:
            cf_res = simulate_counterfactual(base_features, modifications)
            delta_val = cf_res["delta"]
            delta_symbol = "🔺 +" if delta_val > 0 else ("🔻 " if delta_val < 0 else "➖ ")
            delta_color = "#d32f2f" if delta_val > 0 else "#2e7d32"

            st.markdown(
                f"""
                <div style="background-color: white; border: 2px dashed {cf_res['risk_color']}; border-radius: 10px; padding: 18px; margin-top: 10px;">
                    <div style="font-size: 13px; color: #666; font-weight: 700; text-transform: uppercase;">Simulated Counterfactual Outcome</div>
                    <div style="display: flex; align-items: baseline; gap: 15px; margin: 8px 0;">
                        <span style="font-size: 28px; font-weight: 800; color: {cf_res['risk_color']};">
                            {cf_res['simulated_label']} ({cf_res['simulated_prob']}%)
                        </span>
                        <span style="font-size: 18px; font-weight: 700; color: {delta_color};">
                            {delta_symbol}{abs(delta_val)}% Risk Delta
                        </span>
                    </div>
                    <div style="font-size: 13px; color: #444; line-height: 1.4;">
                        <b>Scenario Context:</b> {scenario_description}
                    </div>
                    <div style="font-size: 12px; color: #666; margin-top: 6px;">
                        Baseline Risk: <b>{cf_res['base_prob']}%</b> ➔ Simulated Counterfactual Risk: <b>{cf_res['simulated_prob']}%</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("💡 Select any scenario above to observe real-time mathematical sensitivity of the Random Forest model.")

    # 7. Assessment History Log
    st.divider()
    st.subheader("📜 Previous Assessment Logs")
    assessments = get_all_user_assessments(user_id)
    if assessments:
        df_hist = pd.DataFrame(assessments)
        df_hist = df_hist.rename(columns={
            "id": "Assessment ID",
            "risk_level": "Risk Tier",
            "risk_score": "Risk Probability (%)",
            "model_version": "Model",
            "assessed_at": "Timestamp"
        })
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.caption("No past assessments recorded yet. Run your first assessment above.")
