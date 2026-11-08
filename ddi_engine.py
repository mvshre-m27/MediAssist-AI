"""
Automated Drug-Drug Interaction (DDI) Detection Engine
------------------------------------------------------
Performs pairwise and multi-drug interaction analysis across clinical
regimens, alerting patients and clinicians to adverse pharmacodynamic
and pharmacokinetic drug interactions.
"""

import json
from pathlib import Path
from database import get_connection, get_user_comorbidities
import medicine_food_integration as mfi

DATA_DIR = Path(__file__).parent / "data"
DDI_FILE = DATA_DIR / "drug_interactions_data.json"
DDEI_FILE = DATA_DIR / "disease_interactions_data.json"

_DDI_CACHE = None
_DDEI_CACHE = None

def load_disease_interactions_database():
    """Loads and caches the clinical drug-disease contraindications dataset."""
    global _DDEI_CACHE
    if _DDEI_CACHE is not None:
        return _DDEI_CACHE

    if DDEI_FILE.exists():
        try:
            with open(DDEI_FILE, "r", encoding="utf-8") as f:
                _DDEI_CACHE = json.load(f)
                return _DDEI_CACHE
        except Exception as e:
            print(f"Error loading Drug-Disease interactions: {e}")
            _DDEI_CACHE = []
            return _DDEI_CACHE
    return []

def load_ddi_database():
    """Loads and caches the curated clinical drug-drug interactions dataset."""
    global _DDI_CACHE
    if _DDI_CACHE is not None:
        return _DDI_CACHE

    if DDI_FILE.exists():
        try:
            with open(DDI_FILE, "r", encoding="utf-8") as f:
                _DDI_CACHE = json.load(f)
                return _DDI_CACHE
        except Exception as e:
            print(f"Error loading DDI dataset: {e}")
            _DDI_CACHE = []
            return _DDI_CACHE
    return []


# Class mapping for generalized class-level interactions
DRUG_CLASSES = {
    "ace_inhibitors": ["ramipril", "enalapril", "lisinopril"],
    "arbs": ["telmisartan", "losartan", "valsartan", "olmesartan"],
    "potassium_sparing": ["spironolactone"],
    "statins": ["atorvastatin", "rosuvastatin"],
    "sulfonylureas": ["glimepiride", "gliclazide", "glipizide"],
    "nsaids": ["ibuprofen", "diclofenac", "naproxen"],
    "beta_blockers": ["metoprolol", "atenolol", "bisoprolol", "carvedilol", "nebivolol", "propranolol"],
    "calcium_channel_blockers_non_dhp": ["diltiazem", "verapamil"],
    "dpp4_inhibitors": ["sitagliptin", "vildagliptin", "linagliptin", "teneligliptin"],
    "sglt2_inhibitors": ["dapagliflozin", "empagliflozin", "canagliflozin"],
    "ssris": ["escitalopram", "sertraline"]
}


def find_interaction_between_drugs(drug_query_1, drug_query_2):
    """
    Checks if an interaction exists between two drugs (brand or generic).
    Returns interaction dict or None.
    """
    profile_1 = mfi.match_medicine_profile(drug_query_1)
    profile_2 = mfi.match_medicine_profile(drug_query_2)

    if not profile_1 or not profile_2:
        return None

    id_1 = profile_1["id"]
    id_2 = profile_2["id"]

    if id_1 == id_2:
        return None  # Same drug

    ddi_rules = load_ddi_database()

    # 1. Direct pairwise check (bidirectional)
    for rule in ddi_rules:
        r_a = rule["drug_a"]
        r_b = rule["drug_b"]
        if (r_a == id_1 and r_b == id_2) or (r_a == id_2 and r_b == id_1):
            return {
                "drug_1_name": profile_1["name"],
                "drug_2_name": profile_2["name"],
                "severity": rule["severity"],
                "title": rule["title"],
                "mechanism": rule["mechanism"],
                "clinical_effects": rule["clinical_effects"],
                "recommendation": rule["recommendation"]
            }

    # 2. General Class-Level Fallback Rules
    # Rule: ACEI or ARB + Spironolactone -> Severe Hyperkalemia
    is_raas_1 = id_1 in DRUG_CLASSES["ace_inhibitors"] or id_1 in DRUG_CLASSES["arbs"]
    is_raas_2 = id_2 in DRUG_CLASSES["ace_inhibitors"] or id_2 in DRUG_CLASSES["arbs"]
    is_k_spare_1 = id_1 in DRUG_CLASSES["potassium_sparing"]
    is_k_spare_2 = id_2 in DRUG_CLASSES["potassium_sparing"]

    if (is_raas_1 and is_k_spare_2) or (is_raas_2 and is_k_spare_1):
        return {
            "drug_1_name": profile_1["name"],
            "drug_2_name": profile_2["name"],
            "severity": "Severe",
            "title": "Dual RAAS & Potassium-Sparing Hyperkalemia Risk",
            "mechanism": "Additive inhibition of renal potassium excretion via aldosterone antagonism.",
            "clinical_effects": "Severe hyperkalemia, cardiac arrhythmias, muscle weakness.",
            "recommendation": "Frequent monitoring of serum potassium and renal function (creatinine) is mandatory."
        }

    # Rule: ACEI or ARB + NSAID -> Acute Kidney Injury & Loss of BP Control
    is_nsaid_1 = id_1 in DRUG_CLASSES["nsaids"]
    is_nsaid_2 = id_2 in DRUG_CLASSES["nsaids"]
    if (is_raas_1 and is_nsaid_2) or (is_raas_2 and is_nsaid_1):
        return {
            "drug_1_name": profile_1["name"],
            "drug_2_name": profile_2["name"],
            "severity": "Major",
            "title": "Renal Impairment & Loss of Antihypertensive Efficacy",
            "mechanism": "NSAIDs constrict afferent renal arterioles, while ACEI/ARBs dilate efferent arterioles, collapsing glomerular filtration pressure.",
            "clinical_effects": "Acute kidney injury (AKI), fluid retention, elevated blood pressure.",
            "recommendation": "Avoid chronic NSAIDs. Use Paracetamol for pain relief or monitor creatinine closely."
        }

    # Rule: Beta Blocker + Non-DHP CCB -> Bradycardia / Heart Block
    is_bb_1 = id_1 in DRUG_CLASSES["beta_blockers"]
    is_bb_2 = id_2 in DRUG_CLASSES["beta_blockers"]
    is_nondhp_1 = id_1 in DRUG_CLASSES["calcium_channel_blockers_non_dhp"]
    is_nondhp_2 = id_2 in DRUG_CLASSES["calcium_channel_blockers_non_dhp"]
    if (is_bb_1 and is_nondhp_2) or (is_bb_2 and is_nondhp_1):
        return {
            "drug_1_name": profile_1["name"],
            "drug_2_name": profile_2["name"],
            "severity": "Severe",
            "title": "Compounded AV Nodal Blockade & Refractory Bradycardia",
            "mechanism": "Dual suppression of cardiac pacemaking and atrioventricular conduction.",
            "clinical_effects": "Profound bradycardia, heart block, cardiogenic shock, syncope.",
            "recommendation": "Avoid co-administration unless closely monitored by an electrophysiologist or cardiologist."
        }

    # Rule: Sulfonylurea + Beta Blocker -> Hypoglycemia Masking
    is_su_1 = id_1 in DRUG_CLASSES["sulfonylureas"]
    is_su_2 = id_2 in DRUG_CLASSES["sulfonylureas"]
    if (is_su_1 and is_bb_2) or (is_bb_1 and is_su_2):
        return {
            "drug_1_name": profile_1["name"],
            "drug_2_name": profile_2["name"],
            "severity": "Major",
            "title": "Masking of Hypoglycemia Symptoms",
            "mechanism": "Beta-blockers suppress adrenergic autonomic warning signs (tachycardia, tremor), except sweating.",
            "clinical_effects": "Delayed awareness of low blood sugar, prolonged neuroglycopenia.",
            "recommendation": "Instruct patient that diaphoresis (sweating) remains the primary warning symptom; maintain regular blood sugar checks."
        }

    # Rule: SSRI + NSAID -> Gastrointestinal Bleeding
    is_ssri_1 = id_1 in DRUG_CLASSES["ssris"]
    is_ssri_2 = id_2 in DRUG_CLASSES["ssris"]
    if (is_ssri_1 and is_nsaid_2) or (is_nsaid_1 and is_ssri_2):
        return {
            "drug_1_name": profile_1["name"],
            "drug_2_name": profile_2["name"],
            "severity": "Major",
            "title": "Increased Gastrointestinal Hemorrhage Risk",
            "mechanism": "Dual inhibition of platelet aggregation (serotonin depletion + COX-1 suppression).",
            "clinical_effects": "3- to 5-fold higher rate of upper GI bleeding, peptic ulcers.",
            "recommendation": "Co-prescribe a gastroprotective proton pump inhibitor (Pantoprazole) or switch to Paracetamol."
        }

    return None


def check_patient_regimen_interactions(user_id):
    """
    Scans the patient's currently prescribed active medications in SQLite
    and performs an exhaustive all-pairs DDI analysis.
    """
    user_meds = mfi.get_user_active_medicines(user_id)
    med_names = [m["medicine_name"] for m in user_meds]

    interactions = []
    seen_pairs = set()

    n = len(med_names)
    for i in range(n):
        for j in range(i + 1, n):
            pair_key = tuple(sorted([med_names[i].lower(), med_names[j].lower()]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            inter = find_interaction_between_drugs(med_names[i], med_names[j])
            if inter:
                inter["prescribed_med_1"] = med_names[i]
                inter["prescribed_med_2"] = med_names[j]
                interactions.append(inter)

    # Sort: Severe first, then Major, then Moderate, then Minor
    severity_order = {"Severe": 0, "Major": 1, "Moderate": 2, "Minor": 3}
    interactions.sort(key=lambda x: severity_order.get(x["severity"], 99))

    severe_count = sum(1 for x in interactions if x["severity"] == "Severe")
    major_count = sum(1 for x in interactions if x["severity"] == "Major")
    moderate_count = sum(1 for x in interactions if x["severity"] == "Moderate")
    minor_count = sum(1 for x in interactions if x["severity"] == "Minor")

    return {
        "user_id": user_id,
        "active_med_count": len(user_meds),
        "has_interactions": len(interactions) > 0,
        "total_interactions": len(interactions),
        "severe_count": severe_count,
        "major_count": major_count,
        "moderate_count": moderate_count,
        "minor_count": minor_count,
        "interactions": interactions
    }


def check_new_drug_against_regimen(user_id, new_drug_name):
    """
    Proactively checks a proposed new medicine against the patient's existing regimen.
    Used before adding a medicine in the UI.
    """
    if not new_drug_name or not str(new_drug_name).strip():
        return []

    user_meds = mfi.get_user_active_medicines(user_id)
    warnings = []

    for med in user_meds:
        existing_name = med["medicine_name"]
        inter = find_interaction_between_drugs(new_drug_name, existing_name)
        if inter:
            inter["existing_medicine"] = existing_name
            inter["new_medicine"] = new_drug_name
            warnings.append(inter)

    severity_order = {"Severe": 0, "Major": 1, "Moderate": 2, "Minor": 3}
    warnings.sort(key=lambda x: severity_order.get(x["severity"], 99))
    return warnings


def analyze_custom_medication_list(medicine_list):
    """
    Analyzes an arbitrary list of medications chosen by a clinician or patient.
    Returns list of pairwise interactions and summary statistics.
    """
    valid_names = [m for m in medicine_list if m and str(m).strip()]
    interactions = []
    seen = set()

    for i in range(len(valid_names)):
        for j in range(i + 1, len(valid_names)):
            pair = tuple(sorted([valid_names[i].lower(), valid_names[j].lower()]))
            if pair in seen:
                continue
            seen.add(pair)

            inter = find_interaction_between_drugs(valid_names[i], valid_names[j])
            if inter:
                interactions.append(inter)

    severity_order = {"Severe": 0, "Major": 1, "Moderate": 2, "Minor": 3}
    interactions.sort(key=lambda x: severity_order.get(x["severity"], 99))

    return {
        "total_drugs_checked": len(valid_names),
        "total_interactions": len(interactions),
        "severe_count": sum(1 for x in interactions if x["severity"] == "Severe"),
        "major_count": sum(1 for x in interactions if x["severity"] == "Major"),
        "moderate_count": sum(1 for x in interactions if x["severity"] == "Moderate"),
        "minor_count": sum(1 for x in interactions if x["severity"] == "Minor"),
        "interactions": interactions
    }


def check_patient_drug_disease_interactions(user_id):
    """
    Evaluates patient's active prescribed medications against their diagnosed chronic comorbidities.
    Returns list of identified clinical contraindications.
    """
    user_meds = mfi.get_user_active_medicines(user_id)
    user_comorbidities = get_user_comorbidities(user_id)

    if not user_meds or not user_comorbidities:
        return {
            "has_interactions": False,
            "total_interactions": 0,
            "severe_count": 0,
            "major_count": 0,
            "interactions": []
        }

    comorbidity_keys = {c["condition_key"] for c in user_comorbidities}
    comorbidity_name_map = {c["condition_key"]: c["condition_name"] for c in user_comorbidities}

    ddei_rules = load_disease_interactions_database()
    matched_clashes = []

    for med in user_meds:
        med_name = med["medicine_name"]
        profile = mfi.match_medicine_profile(med_name)
        if not profile:
            continue
        med_id = profile["id"]

        for rule in ddei_rules:
            if rule["drug_id"] == med_id and rule["disease_key"] in comorbidity_keys:
                matched_clashes.append({
                    "prescribed_med": med_name,
                    "matched_drug_name": profile["name"],
                    "disease_key": rule["disease_key"],
                    "disease_name": comorbidity_name_map.get(rule["disease_key"], rule["disease_name"]),
                    "severity": rule["severity"],
                    "title": rule["title"],
                    "mechanism": rule["mechanism"],
                    "clinical_effects": rule["clinical_effects"],
                    "action_plan": rule["action_plan"]
                })

    severity_order = {"Severe": 0, "Major": 1, "Moderate": 2, "Minor": 3}
    matched_clashes.sort(key=lambda x: severity_order.get(x["severity"], 99))

    return {
        "has_interactions": len(matched_clashes) > 0,
        "total_interactions": len(matched_clashes),
        "severe_count": sum(1 for x in matched_clashes if x["severity"] == "Severe"),
        "major_count": sum(1 for x in matched_clashes if x["severity"] == "Major"),
        "interactions": matched_clashes
    }


def check_new_drug_against_diseases(user_id, new_drug_name):
    """
    Checks if a proposed new medicine is contraindicated by any of the patient's diagnosed comorbidities.
    """
    if not new_drug_name or not str(new_drug_name).strip():
        return []

    profile = mfi.match_medicine_profile(new_drug_name)
    if not profile:
        return []
    med_id = profile["id"]

    user_comorbidities = get_user_comorbidities(user_id)
    if not user_comorbidities:
        return []

    comorbidity_keys = {c["condition_key"] for c in user_comorbidities}
    comorbidity_name_map = {c["condition_key"]: c["condition_name"] for c in user_comorbidities}

    ddei_rules = load_disease_interactions_database()
    warnings = []

    for rule in ddei_rules:
        if rule["drug_id"] == med_id and rule["disease_key"] in comorbidity_keys:
            warnings.append({
                "proposed_med": new_drug_name,
                "matched_drug_name": profile["name"],
                "disease_name": comorbidity_name_map.get(rule["disease_key"], rule["disease_name"]),
                "severity": rule["severity"],
                "title": rule["title"],
                "mechanism": rule["mechanism"],
                "clinical_effects": rule["clinical_effects"],
                "action_plan": rule["action_plan"]
            })

    severity_order = {"Severe": 0, "Major": 1, "Moderate": 2, "Minor": 3}
    warnings.sort(key=lambda x: severity_order.get(x["severity"], 99))
    return warnings
