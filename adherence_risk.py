import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection
from adherence_history import get_adherence_data, calculate_adherence
import sys
from pathlib import Path

# Ensure ml directory is on sys.path
ML_DIR = Path(__file__).resolve().parent / "ml"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from predict_risk import (
    predict_adherence_risk,
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

    return {
        "name": name,
        "age": age,
        "med_count": med_count,
        "daily_doses": daily_doses,
        "estimated_units": estimated_units
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
    st.caption("Powered by Machine Learning (Random Forest Pipeline, ROC-AUC: 0.9006, Mendeley Adherence Cohort)")

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
        # Check historical adherence from past 15 days
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

            primary_condition = st.selectbox(
                "Primary Chronic Condition",
                ["Hypertension (High Blood Pressure)", "Type 2 Diabetes", "Both Hypertension & Diabetes"],
                help="Mendeley research shows adherence dynamics differ between asymptomatic conditions (Hypertension) and symptomatic meal-linked conditions (Diabetes)."
            )

            comorbidity_status = st.selectbox(
                "Other Chronic Comorbidities?",
                ["No additional chronic comorbidities", "Yes, has other comorbidities (Cardiovascular, Kidney, etc.)"]
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

            # Persist to SQLite
            assessment_id = save_assessment_to_db(
                user_id=user_id,
                risk_level=result["risk_level"],
                risk_score=result["non_adherence_probability"]
            )

        st.success(f"Assessment complete! Logged as Assessment #{assessment_id}")

        # 3. Prediction Presentation
        res_col1, res_col2 = st.columns([1, 2])

        with res_col1:
            st.markdown(
                f"""
                <div style="background-color: white; border: 2px solid {result['risk_color']}; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 14px; color: #666; text-transform: uppercase; font-weight: 600;">Predicted Risk Tier</div>
                    <div style="font-size: 32px; font-weight: 800; color: {result['risk_color']}; margin: 8px 0;">
                        {result['risk_label']}
                    </div>
                    <div style="font-size: 14px; color: #444;">Non-Adherence Probability: <b>{result['non_adherence_probability']}%</b></div>
                    <div style="font-size: 13px; color: #777; margin-top: 4px;">Adherence Likelihood: <b>{result['adherence_probability']}%</b></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with res_col2:
            st.subheader("🔍 Contributing Clinical Factors")
            for factor in result["contributing_factors"]:
                st.markdown(f"- {factor}")

        st.divider()

        st.subheader("💡 Recommended Supportive Action Plan")
        for tip in result["supportive_advice"]:
            st.info(f"👉 {tip}")

    # 4. Assessment History Log
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
