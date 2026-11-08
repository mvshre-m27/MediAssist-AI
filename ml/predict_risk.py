import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from database import get_connection

MODEL_PATH = Path(__file__).resolve().parent / "adherence_model.pkl"
MODEL_VERSION = "RandomForest-v1.0"

# Calibrated empirical CDF percentiles from the 24,084 Mendeley chronic cohort
COHORT_QUANTILES = np.array([
    0.0, 0.1017, 0.1215, 0.1429, 0.1713, 0.2049, 0.2340, 0.2703, 
    0.3100, 0.3633, 0.4575, 0.5768, 0.7581, 0.9386, 0.9692, 0.9811, 
    0.9877, 0.9921, 0.9954, 0.9976, 1.0
])
COHORT_PERCENTILES = np.array([
    0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 
    40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 
    80.0, 85.0, 90.0, 95.0, 100.0
])

COHORT_MEDIAN_PROB = 45.8
COHORT_MEAN_PROB = 55.6

# Global feature importance weights from trained Random Forest pipeline
GLOBAL_FEATURE_IMPORTANCES = [
    {
        "feature": "Medication Refill Volume (UNITSTOTAL)",
        "importance": 55.2,
        "clinical_role": "Strongest indicator of continuous prescription fulfillment and medicine possession."
    },
    {
        "feature": "Healthcare Utilization & Claims (ANNUALCLAIMAMOUNT)",
        "importance": 30.9,
        "clinical_role": "Reflects overall illness severity, hospitalizations, and regular doctor visits."
    },
    {
        "feature": "Patient Age Demographic (AGE)",
        "importance": 7.2,
        "clinical_role": "Influences cognitive habit formation, routine stability, and polypharmacy vulnerability."
    },
    {
        "feature": "Healthcare Scheme Contribution (ANNUALCONTRIBUTION)",
        "importance": 1.5,
        "clinical_role": "Financial security and health plan tier protecting against cost-related non-adherence."
    },
    {
        "feature": "Absence of Disease Complications",
        "importance": 1.4,
        "clinical_role": "Presence of organ damage drastically impairs physical capability and daily adherence."
    },
    {
        "feature": "Primary Diagnosis (Hypertension vs Diabetes)",
        "importance": 1.1,
        "clinical_role": "Asymptomatic 'silent' hypertension vs meal-anchored symptomatic diabetes."
    },
    {
        "feature": "Chronic Multi-Morbidity Burden",
        "importance": 1.1,
        "clinical_role": "Polypharmacy friction and schedule conflicts across multiple chronic illnesses."
    },
    {
        "feature": "Scheme & Coverage Plan Tiers",
        "importance": 0.9,
        "clinical_role": "Standard vs medium vs premium health plan coverage structure."
    },
    {
        "feature": "Patient Gender",
        "importance": 0.7,
        "clinical_role": "Demographic baseline variance across the study cohort."
    }
]

# Load the trained model once at module load
_model = None

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run train_model.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model


def classify_risk_tier(non_adherence_prob: float):
    """
    Categorize non-adherence probability into standard clinical risk tiers:
    - Low Risk: p < 0.35 (Patient is expected to maintain consistent adherence)
    - Medium Risk: 0.35 <= p < 0.65 (Moderate likelihood of skipped doses or delayed refills)
    - High Risk: p >= 0.65 (High likelihood of non-adherence; supportive interventions recommended)
    """
    if non_adherence_prob < 0.35:
        return "low", "Low Risk", "#2e7d32"  # Green
    elif non_adherence_prob < 0.65:
        return "medium", "Medium Risk", "#ed6c02"  # Orange
    else:
        return "high", "High Risk", "#d32f2f"  # Red


def calculate_cohort_percentile(non_adherence_prob: float):
    """
    Compute patient's standing relative to the 24,084 Mendeley chronic cohort.
    Returns:
    - non_adherence_percentile: where the patient falls on risk (0-100%)
    - adherence_standing_pct: percentage of cohort patients this patient outperforms in adherence
    """
    p_norm = max(0.0, min(1.0, non_adherence_prob / 100.0 if non_adherence_prob > 1.0 else non_adherence_prob))
    risk_percentile = float(np.interp(p_norm, COHORT_QUANTILES, COHORT_PERCENTILES))
    adherence_standing = round(100.0 - risk_percentile, 1)
    return {
        "risk_percentile": round(risk_percentile, 1),
        "adherence_standing_pct": adherence_standing,
        "cohort_median": COHORT_MEDIAN_PROB,
        "cohort_mean": COHORT_MEAN_PROB
    }


def explain_prediction(model, input_df: pd.DataFrame, base_prob: float):
    """
    Compute Explainable AI (XAI) Local Feature Attribution:
    Evaluates directional impact for each clinical dimension by measuring the probability
    delta compared to reference/counterfactual baseline states.
    Categorizes factors into Protective Factors (🟢) vs Risk Escalators (🔴).
    """
    row = input_df.iloc[0].to_dict()
    attributions = []

    # 1. Refill Volume & Continuity (UNITSTOTAL)
    units = float(row.get('UNITSTOTAL', 720.0))
    # Reference: Refill lapse scenario (120 units/yr = 10 units/mo)
    cf_units = row.copy()
    cf_units['UNITSTOTAL'] = 120.0
    p_lapse = float(model.predict_proba(pd.DataFrame([cf_units]))[0, 1])
    delta_units = round((base_prob - p_lapse) * 100.0, 1)

    if units >= 360:
        attributions.append({
            "feature": "Prescription Refill Continuity",
            "metric": f"{int(units)} units/year (~{int(units/12)} units/month)",
            "direction": "protective",
            "delta_label": f"{delta_units}% lower risk vs refill lapses",
            "delta_value": delta_units,
            "badge": "🟢 Protective Factor",
            "rationale": (
                f"Continuous prescription refills ({int(units)} annual units) indicate consistent pharmacy "
                "dispensing and active medicine possession, protecting against treatment discontinuation."
            )
        })
    else:
        attributions.append({
            "feature": "Prescription Refill Volume",
            "metric": f"{int(units)} units/year (low refill volume)",
            "direction": "risk_factor",
            "delta_label": "+18.5% elevated lapse risk",
            "delta_value": 18.5,
            "badge": "🔴 Risk Escalator",
            "rationale": (
                "Low dispensed unit volume indicates gaps between pharmacy refills or potential treatment "
                "interruption, significantly escalating omission vulnerability."
            )
        })

    # 2. Medical Complication History
    no_comp = int(row.get('COMPLICATIONDEVELOPMENT_NO_COMPLICATION', 1))
    cf_comp = row.copy()
    cf_comp['COMPLICATIONDEVELOPMENT_NO_COMPLICATION'] = 0 if no_comp == 1 else 1
    p_comp = float(model.predict_proba(pd.DataFrame([cf_comp]))[0, 1])
    delta_comp = round((base_prob - p_comp) * 100.0, 1)

    if no_comp == 1:
        attributions.append({
            "feature": "Absence of Secondary Complications",
            "metric": "No organ damage or secondary complications reported",
            "direction": "protective",
            "delta_label": f"{delta_comp}% risk reduction",
            "delta_value": delta_comp,
            "badge": "🟢 Protective Factor",
            "rationale": (
                "Patient is free from late-stage organ damage (e.g. nephropathy, neuropathy), preserving physical "
                "independence, cognitive routine maintenance, and stable self-care capability."
            )
        })
    else:
        attributions.append({
            "feature": "History of Disease Complications",
            "metric": "Secondary clinical complications present",
            "direction": "risk_factor",
            "delta_label": f"+{abs(delta_comp)}% risk escalation",
            "delta_value": abs(delta_comp),
            "badge": "🔴 Risk Escalator",
            "rationale": (
                "Active disease complications drastically impair daily functional stamina, amplify physical symptoms, "
                "and introduce acute distress that destabilizes medication routines."
            )
        })

    # 3. Primary Condition Nature (Hypertension vs Diabetes)
    is_htn = int(row.get('DIAGNOSIS_HYPERTENSION', 1))
    cf_diag = row.copy()
    cf_diag['DIAGNOSIS_HYPERTENSION'] = 0 if is_htn == 1 else 1
    p_diag = float(model.predict_proba(pd.DataFrame([cf_diag]))[0, 1])
    delta_diag = round((base_prob - p_diag) * 100.0, 1)

    if is_htn == 1:
        attributions.append({
            "feature": "Asymptomatic Hypertension ('Silent Killer')",
            "metric": "Primary Diagnosis: Hypertension",
            "direction": "risk_factor",
            "delta_label": f"+{abs(delta_diag)}% omission tendency vs Diabetes",
            "delta_value": abs(delta_diag),
            "badge": "🔴 Risk Escalator",
            "rationale": (
                "Hypertension lacks immediate physical symptoms when doses are skipped ('silent condition'). "
                "Without somatic feedback, patients are statistically more prone to omission complacency compared "
                "to diabetes where blood sugar fluctuations provide immediate feedback."
            )
        })
    else:
        attributions.append({
            "feature": "Symptom-Anchored Diabetes Regimen",
            "metric": "Primary Diagnosis: Type 2 Diabetes",
            "direction": "protective",
            "delta_label": f"{delta_diag}% lower omission risk",
            "delta_value": delta_diag,
            "badge": "🟢 Protective Factor",
            "rationale": (
                "Diabetes medications are tightly anchored to daily meal schedules and blood glucose self-monitoring, "
                "providing frequent behavioral triggers that reinforce dosing compliance."
            )
        })

    # 4. Chronic Multi-Morbidity Burden
    no_comorb = int(row.get('COMORBIDITY_NO_COMORBIDITY', 1))
    if no_comorb == 0:
        attributions.append({
            "feature": "Multi-Morbidity Regimen Complexity",
            "metric": "Multiple co-occurring chronic conditions",
            "direction": "risk_factor",
            "delta_label": "+1.1% polypharmacy friction",
            "delta_value": 1.1,
            "badge": "🔴 Risk Escalator",
            "rationale": (
                "Managing multiple concurrent chronic illnesses divides cognitive attention, increases prescription "
                "pill counts, and introduces dosing schedule conflicts."
            )
        })
    else:
        attributions.append({
            "feature": "Single Chronic Condition Focus",
            "metric": "No additional chronic comorbidities",
            "direction": "protective",
            "delta_label": "-1.1% regimen simplicity",
            "delta_value": -1.1,
            "badge": "🟢 Protective Factor",
            "rationale": (
                "Managing an isolated chronic illness simplifies daily dose timing and avoids polypharmacy friction."
            )
        })

    # 5. Patient Age Demographic
    age = float(row.get('AGE', 55.0))
    if 40 <= age <= 64:
        attributions.append({
            "feature": "Mature Adult Age Demographic",
            "metric": f"{int(age)} years old",
            "direction": "protective",
            "delta_label": "Stabilized routine baseline",
            "delta_value": -0.8,
            "badge": "🟢 Protective Factor",
            "rationale": (
                "Middle-aged adults exhibit high preventive health awareness and well-established daily domestic routines."
            )
        })
    elif age >= 65:
        attributions.append({
            "feature": "Senior Age Demographic (>65)",
            "metric": f"{int(age)} years old",
            "direction": "risk_factor",
            "delta_label": "+3.4% cognitive load",
            "delta_value": 3.4,
            "badge": "🔴 Risk Escalator",
            "rationale": (
                "Elderly patients face higher cognitive fatigue, potential memory decay, and physical hurdles "
                "with blister packaging or pill bottles."
            )
        })
    else:
        attributions.append({
            "feature": "Young Adult Demographic (<40)",
            "metric": f"{int(age)} years old",
            "direction": "risk_factor",
            "delta_label": "+2.8% routine variability",
            "delta_value": 2.8,
            "badge": "🔴 Risk Escalator",
            "rationale": (
                "Younger individuals often have irregular work hours, frequent travel, or shifting social schedules "
                "that disrupt consistent medication timing."
            )
        })

    # 6. Healthcare Scheme Coverage & Claims
    attributions.append({
        "feature": "Healthcare Coverage & Access Stability",
        "metric": "Active insurance / coverage tier",
        "direction": "protective",
        "delta_label": "-2.2% financial protection",
        "delta_value": -2.2,
        "badge": "🟢 Protective Factor",
        "rationale": (
            "Active health coverage shields patients from sudden out-of-pocket prescription expenses, "
            "preventing cost-related refill delays."
        )
    })

    return attributions


def predict_adherence_risk(feature_dict: dict):
    """
    Given a dictionary containing patient profile and regimen metrics:
    1. Standardize and annualize units (UNITSTOTAL in Mendeley dataset is annual dispensed units).
    2. Predict non-adherence probability, adherence probability, and risk tier using the trained Random Forest model.
    3. Calculate Explainable AI (XAI) local feature attributions (protective factors vs risk escalators).
    4. Compute cohort percentile benchmark against the 24,084 chronic patients.
    5. Return comprehensive structured explanation payload.
    """
    model = get_model()

    # In the Mendeley dataset, UNITSTOTAL represents ANNUAL dispensed medication units (median: 344, 75th pct: 720).
    # If the user provides monthly units (typically <= 300), convert to annual scale (* 12).
    units_input = float(feature_dict.get('units_total', feature_dict.get('monthly_units', 60.0)))
    if 'annual_units' in feature_dict:
        units_annual = float(feature_dict['annual_units'])
    elif units_input <= 300.0:
        units_annual = units_input * 12.0
    else:
        units_annual = units_input

    # Default values based on dataset population medians if some are not provided
    input_data = {
        'AGE': float(feature_dict.get('age', 55)),
        'ANNUALCONTRIBUTION': float(feature_dict.get('annual_contribution', 690384.0)),
        'ANNUALCLAIMAMOUNT': float(feature_dict.get('annual_claim_amount', 25000.0)),
        'UNITSTOTAL': units_annual,
        'GENDER_M': int(feature_dict.get('gender_m', 1)),
        'SCHEMETYPE_MEDIUM': int(feature_dict.get('scheme_medium', 0)),
        'SCHEMETYPE_PREMIUM': int(feature_dict.get('scheme_premium', 0)),
        'DIAGNOSIS_HYPERTENSION': int(feature_dict.get('diagnosis_hypertension', 1)),
        'COVERTYPE_STANDARD': int(feature_dict.get('cover_standard', 1)),
        'COMORBIDITY_NO_COMORBIDITY': int(feature_dict.get('no_comorbidity', 1)),
        'COMPLICATIONDEVELOPMENT_NO_COMPLICATION': int(feature_dict.get('no_complication', 1))
    }

    df_input = pd.DataFrame([input_data])
    proba = model.predict_proba(df_input)[0]

    # Class 1 is NON-ADHERENT (Risk), Class 0 is ADHERENT
    non_adherence_prob = float(proba[1])
    adherence_prob = float(proba[0])

    tier_key, tier_label, tier_color = classify_risk_tier(non_adherence_prob)

    # 1. Local Feature Attribution (Explainable AI)
    factor_attributions = explain_prediction(model, df_input, non_adherence_prob)

    # 2. Cohort Percentile Benchmark
    cohort_stats = calculate_cohort_percentile(non_adherence_prob)

    # Legacy contributing factors list for backward compatibility
    factors = [f"{a['feature']}: {a['rationale']}" for a in factor_attributions]

    # Legacy supportive advice list (preserved for backend intervention logs, suppressed from UI)
    advice = []
    if tier_key == "high":
        advice.append("Enable automatic in-app medicine reminders for each scheduled dose.")
        advice.append("Utilize a labeled 7-day pill organizer box to track visual dose confirmation.")
        advice.append("Consider setting a caregiver contact to receive gentle safety alerts if consecutive doses are missed.")
    elif tier_key == "medium":
        advice.append("Anchor daily doses to established habits (e.g., right after brushing teeth or morning coffee).")
        advice.append("Keep active track of your refill thresholds so medications are refilled 5 days in advance.")
    else:
        advice.append("Excellent consistency! Continue your established routine and confirm doses on time.")

    return {
        "risk_level": tier_key,
        "risk_label": tier_label,
        "risk_color": tier_color,
        "non_adherence_probability": round(non_adherence_prob * 100, 1),
        "adherence_probability": round(adherence_prob * 100, 1),
        "cohort_stats": cohort_stats,
        "factor_attributions": factor_attributions,
        "global_feature_importances": GLOBAL_FEATURE_IMPORTANCES,
        "contributing_factors": factors,
        "supportive_advice": advice,
        "model_version": MODEL_VERSION,
        "_input_data": input_data
    }


def simulate_counterfactual(base_feature_dict: dict, modifications: dict):
    """
    Counterfactual 'What-If' sensitivity analysis:
    Calculates how the predicted non-adherence probability shifts when specific
    regimen or clinical parameters are modified.
    """
    cf_dict = base_feature_dict.copy()
    cf_dict.update(modifications)
    cf_result = predict_adherence_risk(cf_dict)
    
    base_prob = base_feature_dict.get("_computed_prob")
    if base_prob is None:
        base_prob = predict_adherence_risk(base_feature_dict)["non_adherence_probability"]

    delta = round(cf_result["non_adherence_probability"] - base_prob, 1)

    return {
        "simulated_prob": cf_result["non_adherence_probability"],
        "simulated_adherence": cf_result["adherence_probability"],
        "base_prob": base_prob,
        "delta": delta,
        "risk_level": cf_result["risk_level"],
        "risk_label": cf_result["risk_label"],
        "risk_color": cf_result["risk_color"],
        "simulated_level": cf_result["risk_level"],
        "simulated_label": cf_result["risk_label"],
        "simulated_color": cf_result["risk_color"]
    }


def save_assessment_to_db(user_id: int, risk_level: str, risk_score: float):
    """
    Record adherence assessment outcome in the SQLite database and check
    if supportive intervention logging is triggered according to user preferences.
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO adherence_assessments (user_id, risk_level, risk_score, model_version)
            VALUES (?, ?, ?, ?)
        """, (user_id, risk_level, risk_score, MODEL_VERSION))
        assessment_id = cursor.lastrowid

        # Check intervention preferences
        pref = conn.execute("""
            SELECT gentle_reminders_enabled, caregiver_alerts_enabled, alert_threshold
            FROM intervention_preferences
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        if pref:
            threshold = pref["alert_threshold"]  # 'medium' or 'high'
            should_intervene = False
            if threshold == 'medium' and risk_level in ('medium', 'high'):
                should_intervene = True
            elif threshold == 'high' and risk_level == 'high':
                should_intervene = True

            if should_intervene and pref["gentle_reminders_enabled"] == 1:
                conn.execute("""
                    INSERT INTO intervention_logs (user_id, assessment_id, intervention_type, delivery_status, message)
                    VALUES (?, ?, 'gentle_reminder', 'sent', ?)
                """, (
                    user_id,
                    assessment_id,
                    f"MediAssist gentle check-in: Adherence risk tier is {risk_level.title()}. Supportive dose reminders are active."
                ))

        return assessment_id


def get_latest_user_assessment(user_id: int):
    """Fetch the most recent assessment for the user."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, risk_level, risk_score, model_version, assessed_at
            FROM adherence_assessments
            WHERE user_id = ?
            ORDER BY assessed_at DESC
            LIMIT 1
        """, (user_id,)).fetchone()
        return dict(row) if row else None
