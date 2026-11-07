import joblib
import pandas as pd
from pathlib import Path
from database import get_connection

MODEL_PATH = Path(__file__).resolve().parent / "adherence_model.pkl"
MODEL_VERSION = "RandomForest-v1.0"

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
    Categorize non-adherence probability into standard risk tiers:
    - Low Risk: p < 0.35 (Patient is expected to maintain consistent adherence)
    - Medium Risk: 0.35 <= p < 0.65 (Moderate likelihood of skipped doses or delayed refills)
    - High Risk: p >= 0.65 (High likelihood of non-adherence; supportive interventions recommended)
    """
    if non_adherence_prob < 0.35:
        return "low", "Low Risk", "#2e7d32" # Green
    elif non_adherence_prob < 0.65:
        return "medium", "Medium Risk", "#ed6c02" # Orange
    else:
        return "high", "High Risk", "#d32f2f" # Red

def predict_adherence_risk(feature_dict: dict):
    """
    Given a dictionary containing patient profile and regimen metrics,
    predict non-adherence probability, risk category, and key explanations.
    """
    model = get_model()

    # Default values based on dataset population medians if some are not provided
    input_data = {
        'AGE': float(feature_dict.get('age', 55)),
        'ANNUALCONTRIBUTION': float(feature_dict.get('annual_contribution', 690384.0)),
        'ANNUALCLAIMAMOUNT': float(feature_dict.get('annual_claim_amount', 25000.0)),
        'UNITSTOTAL': float(feature_dict.get('units_total', 60.0)),
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
    
    # Class 1 is NON-ADHERENT (Risk)
    non_adherence_prob = float(proba[1])
    adherence_prob = float(proba[0])

    tier_key, tier_label, tier_color = classify_risk_tier(non_adherence_prob)

    # Generate evidence-based contributing factors
    factors = []
    if input_data['AGE'] >= 65:
        factors.append("Advanced age (>65) increases regimen complexity and cognitive load.")
    elif input_data['AGE'] < 30:
        factors.append("Younger age demographic is statistically associated with higher variability in routine maintenance.")

    if input_data['UNITSTOTAL'] > 90:
        factors.append(f"High pill burden ({int(input_data['UNITSTOTAL'])} medication units dispensed) significantly elevates missed dose risk.")
    elif input_data['UNITSTOTAL'] < 30:
        factors.append("Lower prescription unit volume reduces daily administration friction.")

    if input_data['COMORBIDITY_NO_COMORBIDITY'] == 0:
        factors.append("Presence of multiple chronic comorbidities increases schedule conflict risk.")

    if input_data['COMPLICATIONDEVELOPMENT_NO_COMPLICATION'] == 0:
        factors.append("History of medical complications necessitates strict adherence vigilance.")

    if input_data['DIAGNOSIS_HYPERTENSION'] == 1:
        factors.append("Hypertension ('the silent condition') frequently suffers from asymptomatic omission.")
    else:
        factors.append("Diabetes requires synchronized timing between meals and medication.")

    # Supportive advice
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
        "contributing_factors": factors,
        "supportive_advice": advice,
        "model_version": MODEL_VERSION
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
            threshold = pref["alert_threshold"] # 'medium' or 'high'
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
