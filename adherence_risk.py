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


import altair as alt

def show_adherence_risk_page(user_id):
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>🎯 Medication Adherence Risk Assessment</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>Explainable AI & Random Forest Classifier (ROC-AUC: 0.90 &bull; Mendeley Chronic Cohort, 24,084 Patients)</p>
    </div>
    """, unsafe_allow_html=True)

    regimen = get_user_regimen_summary(user_id)

    # 1. Quick Stats
    with st.container(border=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Active Medicines", f"{regimen['med_count']}")
        with col_b:
            st.metric("Daily Doses Scheduled", f"{regimen['daily_doses']} doses/day")
        with col_c:
            past_records = get_adherence_data(user_id, days=15)
            if past_records:
                total, taken, missed, unconfirmed, adherence = calculate_adherence(past_records)
                st.metric("Recent 15-Day Adherence", f"{adherence:.0f}%" if (taken + missed) > 0 else "Pending")
            else:
                st.metric("Recent 15-Day Adherence", "N/A")

    # 2. Assessment Form
    st.markdown("#### Patient Regimen & Clinical Inputs")

    with st.form("adherence_ml_form"):
        col1, col2 = st.columns(2)

        with col1:
            patient_age = st.number_input(
                "Patient Age",
                min_value=16,
                max_value=110,
                value=int(regimen["age"]),
                step=1
            )

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
                "Primary Diagnosed Condition",
                ["Hypertension (High Blood Pressure)", "Type 2 Diabetes", "Both Hypertension & Diabetes"],
                index=cond_idx
            )

            comorbidity_status = st.selectbox(
                "Additional Comorbidities?",
                ["No additional chronic comorbidities", "Yes, has other comorbidities (Cardiovascular, Renal, etc.)"],
                index=comorb_idx
            )

        with col2:
            units_dispensed = st.number_input(
                "Estimated Monthly Refill Units (Pills)",
                min_value=10,
                max_value=300,
                value=int(regimen["estimated_units"]),
                step=5
            )

            complications = st.selectbox(
                "Disease Complications History?",
                ["No secondary complications", "Yes, history of complications"]
            )

            coverage_tier = st.selectbox(
                "Healthcare Scheme Coverage Tier",
                ["Standard Plan", "Medium Tier", "Premium / Comprehensive Tier"]
            )

        submitted = st.form_submit_button("⚡ Calculate Non-Adherence Risk", type="primary", use_container_width=True)

    if submitted:
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

        with st.spinner("Executing Random Forest classification pipeline..."):
            result = predict_adherence_risk(feature_dict)
            feature_dict["_computed_prob"] = result["non_adherence_probability"]

            assessment_id = save_assessment_to_db(
                user_id=user_id,
                risk_level=result["risk_level"],
                risk_score=result["non_adherence_probability"]
            )

            st.session_state["adherence_assessment_result"] = result
            st.session_state["adherence_assessment_features"] = feature_dict
            st.session_state["adherence_assessment_id"] = assessment_id

    # 3. Assessment Findings Display
    if "adherence_assessment_result" in st.session_state:
        result = st.session_state["adherence_assessment_result"]
        base_features = st.session_state["adherence_assessment_features"]

        st.markdown("#### Assessment Findings & Risk Stratification")

        res_col1, res_col2 = st.columns([1, 1])

        # Color and label logic
        prob = result['non_adherence_probability']
        if prob <= 33:
            badge_cls = "badge-green"
        elif prob <= 66:
            badge_cls = "badge-amber"
        else:
            badge_cls = "badge-red"

        with res_col1:
            with st.container(border=True):
                st.markdown(f"""
                <div style='text-align: center; padding: 10px 0;'>
                    <div style='font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;'>Predicted Non-Adherence Risk</div>
                    <div style='font-size: 44px; font-weight: 800; color: {result['risk_color']}; line-height: 1.1; margin: 6px 0;'>
                        {prob:.1f}%
                    </div>
                    <span class='badge-pill {badge_cls}' style='font-size: 13px; padding: 4px 14px;'>
                        {result['risk_label']}
                    </span>
                    <div style='margin-top: 14px; font-size: 13px; color: #166534; font-weight: 600;'>
                        Estimated Adherence Likelihood: <b>{result['adherence_probability']}%</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with res_col2:
            cohort = result["cohort_stats"]
            with st.container(border=True):
                st.markdown(f"""
                <div style='padding: 6px 0;'>
                    <div style='font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;'>Cohort Population Standing</div>
                    <div style='font-size: 22px; font-weight: 700; color: #0284c7; margin: 4px 0;'>
                        Top {cohort['adherence_standing_pct']}% Adherence Standing
                    </div>
                    <div style='font-size: 13px; color: #475569; margin-top: 6px; line-height: 1.5;'>
                        &bull; Patient Risk: <b>{result['non_adherence_probability']}%</b><br>
                        &bull; Cohort Median: <b>{cohort['cohort_median']}%</b> &bull; Mean: <b>{cohort['cohort_mean']}%</b><br>
                        &bull; Outperforms <b>{cohort['adherence_standing_pct']}%</b> of 24,084 patients in routine regimen stability.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 4. Explainable AI: Factor Impact Visualization (Altair)
        st.markdown("#### Factor Attribution & Impact Breakdown")
        st.caption("Visualizing the mathematical influence of regimen features on predicted non-adherence probability:")

        chart_factors = []
        for item in result.get("factor_attributions", []):
            is_risk = item["direction"] == "risk_factor"
            # Extract impact value or estimate
            val_text = item.get("delta_label", "")
            try:
                val = float(val_text.replace("+", "").replace("-", "").replace("%", ""))
                val = val if is_risk else -val
            except Exception:
                val = 15.0 if is_risk else -15.0

            chart_factors.append({
                "Feature": item["feature"],
                "Impact": val,
                "Type": "Risk Escalator" if is_risk else "Protective Factor",
                "Rationale": item["rationale"]
            })

        if chart_factors:
            df_attr = pd.DataFrame(chart_factors)
            attr_chart = alt.Chart(df_attr).mark_bar(cornerRadius=4).encode(
                x=alt.X('Impact:Q', title='Impact on Risk Score (%)'),
                y=alt.Y('Feature:N', sort='-x', title=''),
                color=alt.Color('Type:N', scale=alt.Scale(
                    domain=['Protective Factor', 'Risk Escalator'],
                    range=['#10b981', '#ef4444']
                )),
                tooltip=['Feature', 'Impact', 'Type', 'Rationale']
            ).properties(height=200)
            st.altair_chart(attr_chart, use_container_width=True)

        # 5. Interactive "What-If" Counterfactual Sensitivity Simulator
        st.markdown("#### Interactive 'What-If' Scenario Simulator")
        st.caption("Test how changes in medication supply or clinical complexity alter non-adherence probability:")

        sim_option = st.radio(
            "Pre-configured Scenarios:",
            [
                "Baseline (Current Profile)",
                "Scenario A: Supply Disruption (Refill units drop by 75%)",
                "Scenario B: Secondary Complications Emerge",
                "Scenario C: Single-Medication Regimen (Zero polypharmacy)"
            ],
            horizontal=True
        )

        modifications = {}
        if "Scenario A" in sim_option:
            modifications = {"units_total": 15}
        elif "Scenario B" in sim_option:
            modifications = {"no_complication": 0}
        elif "Scenario C" in sim_option:
            modifications = {"no_comorbidity": 1}

        if modifications:
            cf_res = simulate_counterfactual(base_features, modifications)
            delta_val = cf_res["delta"]
            delta_symbol = "🔺 +" if delta_val > 0 else ("🔻 " if delta_val < 0 else "➖ ")
            delta_color = "#ef4444" if delta_val > 0 else "#10b981"

            with st.container(border=True):
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;'>
                    <div>
                        <div style='font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;'>Simulated Counterfactual Risk</div>
                        <div style='font-size: 26px; font-weight: 800; color: {cf_res['risk_color']}; margin-top: 2px;'>
                            {cf_res['simulated_label']} ({cf_res['simulated_prob']}%)
                        </div>
                    </div>
                    <div style='font-size: 20px; font-weight: 700; color: {delta_color};'>
                        {delta_symbol}{abs(delta_val):.1f}% Risk Delta
                    </div>
                </div>
                <div style='font-size: 13px; color: #64748b; margin-top: 8px;'>
                    Baseline Risk: <b>{cf_res['base_prob']}%</b> ➔ Simulated Risk: <b>{cf_res['simulated_prob']}%</b>
                </div>
                """, unsafe_allow_html=True)

    # 6. History Log
    st.markdown("#### Past Assessment Audits")
    assessments = get_all_user_assessments(user_id)
    if assessments:
        df_hist = pd.DataFrame(assessments)
        df_hist = df_hist.rename(columns={
            "id": "ID",
            "risk_level": "Risk Tier",
            "risk_score": "Risk (%)",
            "model_version": "Model",
            "assessed_at": "Timestamp"
        })
        st.dataframe(df_hist, width="stretch", hide_index=True)
    else:
        st.caption("No past assessments recorded yet. Run your first assessment above.")
