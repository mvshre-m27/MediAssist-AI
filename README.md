# MediAssist-AI 💚
### An Intelligent Medication Management, Adherence Risk Prediction & Clinical Dietary Support System

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

**Capstone Project — Samsung Innovation Campus Program**  
**Team Members:**
- Ankitha S (`1DS23IS020`) — *Member 2: Medicine Management, Dose Tracking, Stock & Reminders, Adherence History*
- Shreya MV (`1DS24CD057`) — *Member 1: Core Architecture, Authentication, Database Engine, UI Layout*
- Harshitha R (`1DS24CD019`) — *Member 3: Machine Learning Adherence Pipeline, Dietary Recommender, System Integration*

---

## 📖 1. Project Overview & Problem Statement

Consistent medication taking is critical for patients managing chronic non-communicable diseases such as **Hypertension** and **Type 2 Diabetes**. However, patients frequently struggle with:
1. **Regimen Complexity:** Juggling multiple daily timings across ongoing regular medicines and temporary acute courses.
2. **Stock Depletion:** Running out of essential medications before refilling.
3. **Passive Reminders:** Most standard reminder apps send basic notifications without analyzing historical dose trends or non-adherence risk.
4. **Uncoordinated Dietary Habits:** Chronic care patients often lack dietary guidance aligned with clinical regimens (e.g., DASH diet for blood pressure or Low-GI foods for glycemic control) and allergen safety.

**MediAssist-AI** addresses these challenges in a unified, privacy-first web application combining active medicine management, automated stock deductions, historical adherence tracking, an **offline-trained Machine Learning non-adherence risk classifier (ROC-AUC: 0.90)**, and an **evidence-based clinical nutrition recommendation engine**.

---

## 🌟 2. Key Modules & Features

### A. Authentication & Security
- Salted PBKDF2-HMAC-SHA256 password hashing (600,000 iterations, 16-byte cryptographically secure random salt).
- Session-isolated user profiles and multi-tenant data isolation.

### B. Medicine Management & Stock Sync
- Manage **Regular** (continuous) and **Temporary** (start and end date) medications.
- Multi-dose timing schedules per medicine.
- Total and remaining stock tracking with custom refill threshold alerts.
- Historical schedule protection: Updating medicine details preserves previous dose confirmation logs.

### C. Daily Dose Tracking & Automated Inventory
- Real-time today's dose view with one-click status confirmation (`Taken`, `Missed`, `Unconfirmed`).
- **Automated Stock Deduction:** Decrements inventory by 1 when marked Taken; restores stock if status is reversed.
- Prevents Taken confirmation if stock is 0.

### D. In-App Reminders & Refill Alerts
- Due-dose notifications based on the current time and active schedules.
- Low-stock warning banner when remaining units fall below user-defined refill thresholds.

### E. Adherence Analytics & History
- Recursive SQL query calculating dose compliance over **7, 15, or 30-day windows**.
- Computes confirmed adherence rate:
  $$\text{Adherence Rate (\%)} = \frac{\text{Taken Doses}}{\text{Taken Doses} + \text{Missed Doses}} \times 100$$

### F. ML-Based Medication Adherence Risk Prediction
- Trained on **24,084 patient records** from the **Mendeley Data Chronic Adherence Cohort** (Diabetes & Hypertension).
- Random Forest Classifier with standardized preprocessing pipeline.
- Categorizes patients into **Low Risk**, **Medium Risk**, and **High Risk** tiers.
- Highlights specific clinical risk drivers (pill burden, age, comorbidity, disease type).
- Logs assessment audits to SQLite `adherence_assessments` and triggers supportive check-ins based on user preferences.

### G. Personalized Indian Food & Nutrition Recommender
- Knowledge base of **567 authentic foods** from the **Indian Food Composition Tables (IFCT / ICMR-NIN)** across all 12 categories (Millets, Pulses, Leafy Greens, Vegetables, Roots, Fruits, Nuts, Spices, Dairy, Fish/Egg/Meat, Beverages, Healthy Oils).
- **Two-Layer Recommender:**
  1. *Layer 1 (Zero-Tolerance Safety Filter):* Deterministically excludes declared allergens (`peanuts`, `dairy`, `gluten`, `soy`, `eggs`, `fish`, etc.) and enforces diet type compliance (`Vegetarian`, `Vegan`, `Eggetarian`, `Non-vegetarian`, `Pescatarian`).
  2. *Layer 2 (Multi-Attribute Utility Algorithm):* Dynamically scores and ranks foods based on user health profile (DASH diet for Hypertension, Low-GI for Diabetes, Heart-Healthy).
- **Multi-Morbid Dietary Harmonization:** Resolves conflicting dietary needs across comorbidities:
  - *Renal Safety Override (CKD):* Overrides DASH high-potassium foods (potassium $>250\text{ mg}$ capped) to protect failing kidneys against fatal hyperkalemia.
  - *Purine Safety Override (Gout):* Filters high-purine meats/seafood to prevent uric acid flares while boosting alkalizing foods (cherries, amla, oats, dahi).
  - *Mucosal Protection (GERD/Ulcer):* Filters acidic/spicy triggers (citrus, chili, deep-fried snacks) and promotes alkaline, soothing staples.
- Search bar across English and Hindi local names (e.g. *Palak, Ragi, Methi, Amla, Chana*) and nutrients, responsive pagination (20 foods/page), and full macro/micronutrient breakdown.
- **Drug-Nutrient Integration:** Evaluates patient's active medications to flag food items with 🛑 Contraindicated, ⏱️ Spacing Required, or 🌟 Therapeutic Synergy badges.

### H. Automated Drug-Drug & Drug-Disease Interaction (DDI / DDeI) Checker
- **71 Curated Chronic Disease Medications:** Indexed with generic names, Indian brand names (*Glycomet, Amlong, Telma, Atorva, Pan-40, Thyronorm, Dolo 650, Ecosprin, Shelcal*), dosages, and pharmacology summaries.
- **60+ Clinical DDI Rules:** Covers Severe/Contraindicated (e.g., Amlodipine + Clarithromycin, Telmisartan + Spironolactone hyperkalemia, Aspirin + Ibuprofen bleeding, Digoxin + Amiodarone toxicity), Major Precautions (e.g., Clopidogrel + Omeprazole, Beta-blockers + Sulfonylureas, ACEI/ARB + NSAIDs), and Moderate interactions.
- **Drug-Disease Interaction (DDeI) Checker:** Cross-references active prescriptions against diagnosed comorbidities:
  - *Asthma + Non-selective Beta-blockers (Propranolol, Carvedilol):* 🔴 Severe (Severe Bronchospasm & Respiratory Arrest).
  - *CKD + NSAIDs (Ibuprofen, Diclofenac):* 🔴 Severe (Acute-on-Chronic Renal Failure).
  - *Heart Failure + Non-DHP CCBs (Verapamil, Diltiazem) / Glitazones (Pioglitazone):* 🔴 Severe (Decompensated Heart Failure & Pulmonary Edema).
  - *Gout + Thiazide/Loop Diuretics (Chlorthalidone, HCTZ, Furosemide):* 🟠 Major (Hyperuricemia & Gout Attacks).
  - *GERD / Peptic Ulcer + NSAIDs / Aspirin:* 🔴 Severe (Gastric Ulceration & Hemorrhage).
  - *Liver Impairment + Paracetamol:* 🟠 Major (Hepatotoxicity at standard doses).
- **Automated Regimen Audit & Proactive Interception:** Scans active prescriptions in SQLite and intercepts contraindicated additions in real time.
- **Interactive Multi-Drug Simulator:** Tests arbitrary polypharmacy combinations with preset clinical triads.

### I. Diagnosed Comorbidities Tracker & ML Adherence Calibration
- Manage chronic diagnosed conditions under **Profile** (Diabetes, Hypertension, CKD, Heart Failure, Gout, GERD, Asthma, Liver Disease, Dyslipidemia).
- Automatically feeds comorbidity status into the **Random Forest ML pipeline** (`COMORBIDITY_NO_COMORBIDITY`), factoring multi-morbidity burden into the non-adherence risk score.

### J. Settings & Caregiver Safeguards
- Configure intervention thresholds (`High Risk Only` vs `Medium or High Risk`).
- Manage caregiver contacts with verified consent tracking.
- Transparent intervention delivery audit logs.

---

## 🧠 3. Machine Learning Architecture & Evaluation

### Dataset
- **Source:** *Dataset for analysing medication adherence among diabetes and hypertension patients: Patient-level and medication refill data*, Mendeley Data, Version 2, DOI: `10.17632/zkp7sbbx64.2` (CC0 1.0 Public Domain).
- **Size:** 24,084 patient records (14,415 Non-Adherent, 9,669 Adherent).
- **Features:** Patient Age, Dispensed Units (`UNITSTOTAL`), Annual Claims, Annual Contributions, Coverage Tiers, Hypertension vs. Diabetes diagnosis, Comorbidities, and Complication history.

### Model Comparison Benchmark (80/20 Stratified Split)

| Algorithm | ROC-AUC | Accuracy | Precision (Non-Adherent) | Recall (Non-Adherent) | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** (Baseline) | 0.6586 | 61.86% | 69.72% | 64.13% | 0.6681 |
| **Decision Tree** | 0.8893 | 80.59% | 91.95% | 74.05% | 0.8204 |
| **Random Forest Classifier** (Selected) | **0.9006** | **81.03%** | **92.86%** | **73.99%** | **0.8236** |

**Confusion Matrix (Random Forest on Test Set):**
```
[[1770  164]    --> 1770 True Negatives (Adherent correctly identified)
 [ 750 2133]]   --> 2133 True Positives (Non-Adherent correctly identified)
```
- **92.86% Precision** on the risk class minimizes false alarms and alert fatigue.
- Pipeline serialized using Joblib to `ml/adherence_model.pkl`.

---

## 🗄️ 4. Database Schema (SQLite)

The SQLite database (`data/mediassist.db`) maintains 10 normalized tables:

```
users ───────────────┬──< user_profiles
                     ├──< medicines ──< dose_schedules ──< dose_records
                     ├──< food_preferences
                     ├──< intervention_preferences
                     ├──< caregiver_contacts
                     ├──< adherence_assessments ──< intervention_logs
```

1. `users`: Credentials, PBKDF2 hash, and random salt.
2. `user_profiles`: Full name and age.
3. `medicines`: Medicine name, type, instructions, dates, stock, refill threshold, active flag.
4. `dose_schedules`: Daily dose times linked to medicines.
5. `dose_records`: Daily dose confirmation outcomes (`taken`, `missed`, `unconfirmed`).
6. `food_preferences`: Diet types, allergies, dietary restrictions, notes.
7. `intervention_preferences`: Gentle reminder and caregiver alert toggles and threshold.
8. `caregiver_contacts`: Caregiver contact info, consent flag, and enabled status.
9. `adherence_assessments`: ML prediction audit trail (`risk_level`, `risk_score`, `model_version`).
10. `intervention_logs`: Records of supportive check-in messages delivered.

---

## 💻 5. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Windows / macOS / Linux

### 1. Clone or Extract Project
```bash
git clone https://github.com/YourUsername/MediAssist-AI.git
cd MediAssist-AI
```

### 2. Set Up Virtual Environment
```powershell
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Retrain ML Model
The pre-trained model is saved at `ml/adherence_model.pkl`. To retrain from the dataset:
```bash
python ml/train_model.py
```

### 5. Launch Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🛡️ 6. Clinical & Ethical Disclaimers

> [!WARNING]
> **Educational & Decision-Support Notice:**  
> MediAssist-AI is designed strictly as a medication management and adherence-support aid. It does **NOT** provide medical diagnosis, prescribe drugs, modify dosages, or replace consultations with licensed physicians, pharmacists, or registered dietitians.
> 
> The ML risk classification is a statistical prototype estimate derived from chronic patient refill data. Dietary recommendations are general guidelines aligned with ADA/AHA public recommendations and must be personalized by healthcare professionals for individual clinical care.
