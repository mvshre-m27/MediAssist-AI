"""
Generate data/medicines_data.json containing detailed pharmacology, meal timing, 
food interactions, contraindications, and dietary synergies for common medications.
"""
import json
from pathlib import Path

MEDICINES_DATA = [
    # ------------------ DIABETES ------------------
    {
        "id": "metformin",
        "name": "Metformin",
        "brand_names": ["Glycomet", "Glucophage", "Obimet", "Cetapin", "Riomet"],
        "category": "Anti-diabetic (Biguanide)",
        "default_dosage": "500 mg",
        "meal_timing": "Take with or immediately after meals (breakfast/dinner)",
        "food_interactions": {
            "avoid": ["Excessive alcohol (increases risk of lactic acidosis)", "Crash starvation diets"],
            "caution": ["Taking on an empty stomach frequently causes nausea, cramps, and diarrhea"],
            "beneficial": [
                "Vitamin B12-rich foods (milk, curd, eggs, paneer, fortified nutritional yeast) to prevent B12 depletion",
                "High-soluble-fiber foods (oats, barley, fenugreek/methi seeds, ragi) for glycemic stabilization"
            ]
        },
        "critical_alert": "Avoid alcohol consumption. If taking for over 1-2 years, monitor Vitamin B12 levels regularly.",
        "clinical_summary": "Decreases hepatic glucose production and increases insulin sensitivity. Food slows absorption slightly but dramatically improves gastrointestinal tolerance."
    },
    {
        "id": "glimepiride",
        "name": "Glimepiride",
        "brand_names": ["Amaryl", "Glimy", "Zoryl", "Gepride"],
        "category": "Anti-diabetic (Sulfonylurea)",
        "default_dosage": "1 mg or 2 mg",
        "meal_timing": "Take immediately before or with the first substantial meal of the day (usually breakfast)",
        "food_interactions": {
            "avoid": ["Alcohol (severely escalates risk of sudden hypoglycemia)", "Skipping meals"],
            "caution": ["Never take without eating a carbohydrate-containing meal shortly after; risk of dangerous hypoglycemic drops"],
            "beneficial": [
                "Complex unrefined carbohydrates (millets, oats, brown rice, whole wheat) for sustained glucose release",
                "Carry fast-acting carbohydrates (dextrose tablets, raisins, fruit juice) for emergency hypoglycemic relief"
            ]
        },
        "critical_alert": "High risk of hypoglycemia if meals are skipped or delayed. Always eat within 15-30 minutes of taking.",
        "clinical_summary": "Stimulates pancreatic beta-cells to secrete insulin. Must be synchronized with food intake to match insulin release with dietary carbohydrate absorption."
    },
    {
        "id": "gliclazide",
        "name": "Gliclazide",
        "brand_names": ["Diamicron", "Reclide", "Glizid", "Azukon"],
        "category": "Anti-diabetic (Sulfonylurea)",
        "default_dosage": "40 mg or 80 mg (or 30/60 mg MR)",
        "meal_timing": "Take with breakfast or morning meal",
        "food_interactions": {
            "avoid": ["Alcohol", "Skipping breakfast"],
            "caution": ["Do not crush or chew modified release (MR) formulations"],
            "beneficial": ["Fiber-rich breakfast (oats, sprouted moong, vegetable poha) to avoid rapid blood glucose spikes"]
        },
        "critical_alert": "Skipping meals while on Gliclazide can cause severe hypoglycemia.",
        "clinical_summary": "Second-generation sulfonylurea with selective pancreatic beta cell binding; reduces post-meal glycemic excursions when taken with breakfast."
    },
    {
        "id": "sitagliptin",
        "name": "Sitagliptin",
        "brand_names": ["Januvia", "Istavel", "Zita"],
        "category": "Anti-diabetic (DPP-4 Inhibitor)",
        "default_dosage": "50 mg or 100 mg",
        "meal_timing": "May be taken with or without food at the same time each day",
        "food_interactions": {
            "avoid": ["High-glycemic-index sugary foods, sweetened drinks, and refined pastries"],
            "caution": ["Excessive alcohol"],
            "beneficial": ["Low-GI vegetables, legumes, and lean proteins to support GLP-1 inkretin action"]
        },
        "critical_alert": "Low inherent risk of hypoglycemia on its own; risk increases if combined with sulfonylureas or insulin.",
        "clinical_summary": "Inhibits DPP-4 enzyme, prolonging endogenous active incretin hormones (GLP-1 and GIP) which stimulate glucose-dependent insulin release."
    },
    {
        "id": "dapagliflozin",
        "name": "Dapagliflozin",
        "brand_names": ["Forxiga", "Oxra", "Dapaone", "Justo"],
        "category": "Anti-diabetic & Cardiorenal (SGLT2 Inhibitor)",
        "default_dosage": "5 mg or 10 mg",
        "meal_timing": "Take in the morning with or without food",
        "food_interactions": {
            "avoid": ["Severe dehydration, excessive alcohol (risk of ketoacidosis), very low-carbohydrate/keto diets without medical monitoring"],
            "caution": ["Diuretic effect: drink plenty of clean water throughout the day (at least 2-2.5 liters unless fluid restricted)"],
            "beneficial": ["Hydrating foods (cucumber, bottle gourd, buttermilk, clear vegetable soups)"]
        },
        "critical_alert": "Promotes urinary glucose excretion; maintain adequate hydration to prevent volume depletion, orthostatic hypotension, and urinary tract infections.",
        "clinical_summary": "Inhibits sodium-glucose co-transporter 2 in proximal renal tubules, reducing blood glucose and blood pressure while conferring cardioprotective and nephroprotective benefits."
    },
    {
        "id": "empagliflozin",
        "name": "Empagliflozin",
        "brand_names": ["Jardiance", "Gibtulio"],
        "category": "Anti-diabetic & Cardiorenal (SGLT2 Inhibitor)",
        "default_dosage": "10 mg or 25 mg",
        "meal_timing": "Take once daily in the morning with or without food",
        "food_interactions": {
            "avoid": ["Excessive alcohol", "Extreme dehydration"],
            "caution": ["Ensure consistent daily water intake to balance mild osmotic diuresis"],
            "beneficial": ["DASH-diet foods, leafy greens, potassium-balanced vegetables"]
        },
        "critical_alert": "Maintain good hydration and genital hygiene to reduce risk of mycotic infections.",
        "clinical_summary": "Selectively blocks renal glucose reabsorption. Demonstrates proven reduction in cardiovascular death and heart failure hospitalization."
    },
    {
        "id": "pioglitazone",
        "name": "Pioglitazone",
        "brand_names": ["Pio", "Actos", "Piosys"],
        "category": "Anti-diabetic (Thiazolidinedione / PPAR-gamma agonist)",
        "default_dosage": "15 mg or 30 mg",
        "meal_timing": "Take once daily with or without food",
        "food_interactions": {
            "avoid": ["Excessive dietary sodium (worsens fluid retention and peripheral edema)"],
            "caution": ["Watch for sudden weight gain or swelling in ankles/feet"],
            "beneficial": ["Low-sodium foods, fresh vegetables, potassium-rich foods to balance fluid equilibrium"]
        },
        "critical_alert": "Contraindicated in patients with symptomatic heart failure due to potential for fluid retention.",
        "clinical_summary": "Improves target cell response to insulin without increasing pancreatic insulin secretion; promotes adipocyte glucose uptake."
    },

    # ------------------ HYPERTENSION & CARDIOLOGY ------------------
    {
        "id": "amlodipine",
        "name": "Amlodipine",
        "brand_names": ["Norvasc", "Amlong", "Amlopin", "Amlovas", "Stamlo"],
        "category": "Antihypertensive (Calcium Channel Blocker - DHP)",
        "default_dosage": "5 mg",
        "meal_timing": "Take once daily at the same time, with or without food",
        "food_interactions": {
            "avoid": ["Grapefruit and Grapefruit juice (inhibits CYP3A4 metabolism, causing dangerously high drug levels and severe hypotension)"],
            "caution": ["Excessive dietary sodium (counteracts antihypertensive efficacy)", "High alcohol intake"],
            "beneficial": [
                "Potassium-rich vegetables (spinach, ridge gourd, ash gourd) to naturally support endothelial vasodilation",
                "Garlic, hibiscus tea, and dietary nitrate foods (beetroot) for synergistic blood pressure control"
            ]
        },
        "critical_alert": "STRICT WARNING: Do NOT consume grapefruit, seville oranges, or pomelo juice while taking Amlodipine.",
        "clinical_summary": "Relaxes arterial smooth muscle by inhibiting calcium influx into vascular cells. Grapefruit blocks intestinal CYP3A4, multiplying systemic bioavailability unpredictably."
    },
    {
        "id": "telmisartan",
        "name": "Telmisartan",
        "brand_names": ["Telma", "Micardis", "Telpres", "Creser", "Telsar"],
        "category": "Antihypertensive (Angiotensin II Receptor Blocker - ARB)",
        "default_dosage": "40 mg or 80 mg",
        "meal_timing": "Take once daily with or without food at the same time each day",
        "food_interactions": {
            "avoid": ["High-potassium salt substitutes (such as Lona, potassium chloride table salt substitutes) which can lead to life-threatening hyperkalemia"],
            "caution": ["Excessive dietary licorice (can raise BP)", "Excess potassium supplements without blood monitoring"],
            "beneficial": [
                "DASH-diet plant foods with natural minerals, unrefined grains, berries, and moderate natural potassium",
                "Low-sodium culinary seasonings (lemon juice, cumin, coriander, mint) instead of sodium salt"
            ]
        },
        "critical_alert": "Do NOT use potassium-based salt substitutes or potassium supplements without consulting your doctor (risk of hyperkalemia).",
        "clinical_summary": "Selectively blocks AT1 receptor subtype, preventing angiotensin II-induced vasoconstriction and aldosterone secretion. Conserves potassium in renal tubules."
    },
    {
        "id": "losartan",
        "name": "Losartan",
        "brand_names": ["Cozaar", "Repace", "Losacar", "Tozaar"],
        "category": "Antihypertensive (Angiotensin II Receptor Blocker - ARB)",
        "default_dosage": "50 mg",
        "meal_timing": "Take once daily with or without food",
        "food_interactions": {
            "avoid": ["Potassium-enriched salt substitutes", "Excessive potassium dietary supplements"],
            "caution": ["Alcohol may cause dizziness or orthostatic hypotension"],
            "beneficial": ["Low-sodium dietary foods, antioxidant-rich vegetables, flaxseeds"]
        },
        "critical_alert": "Avoid potassium chloride salt alternatives. Monitor serum potassium and creatinine regularly.",
        "clinical_summary": "Competitive antagonist of angiotensin II receptors. Provides renal protection in type 2 diabetic nephropathy in addition to BP control."
    },
    {
        "id": "ramipril",
        "name": "Ramipril",
        "brand_names": ["Cardace", "Altace", "Hopace", "Ramirid"],
        "category": "Antihypertensive (ACE Inhibitor)",
        "default_dosage": "2.5 mg or 5 mg",
        "meal_timing": "Take with or without food, preferably at the same time every morning",
        "food_interactions": {
            "avoid": ["Potassium salt substitutes (KCl)", "Potassium supplements unless specifically prescribed"],
            "caution": ["High intake of dried fruits or potassium-dense juices if kidney function is compromised"],
            "beneficial": ["DASH diet staples: green vegetables, oats, lentils, and fresh fruits with natural moderate potassium"]
        },
        "critical_alert": "ACE inhibitors reduce aldosterone, decreasing potassium excretion. Watch out for hyperkalemia.",
        "clinical_summary": "Suppresses renin-angiotensin-aldosterone system by inhibiting ACE. Slows progression of diabetic nephropathy and post-MI ventricular remodeling."
    },
    {
        "id": "enalapril",
        "name": "Enalapril",
        "brand_names": ["Envas", "Vasotec", "Nuril"],
        "category": "Antihypertensive (ACE Inhibitor)",
        "default_dosage": "5 mg",
        "meal_timing": "Take once or twice daily with or without food",
        "food_interactions": {
            "avoid": ["Potassium chloride salt substitutes"],
            "caution": ["Dehydration or heavy sweating increases risk of hypotension"],
            "beneficial": ["Balanced hydration and low-sodium home cooked meals"]
        },
        "critical_alert": "Do not substitute normal salt with potassium-based 'low-sodium' salts without checking serum potassium.",
        "clinical_summary": "Prodrug bioactivated to enalaprilat, decreasing systemic vascular resistance and left ventricular afterload."
    },
    {
        "id": "metoprolol",
        "name": "Metoprolol",
        "brand_names": ["Betaloc", "Seloken", "Metolar", "Prolomet"],
        "category": "Cardiovascular (Beta-1 Selective Blocker)",
        "default_dosage": "25 mg or 50 mg (Succinate ER or Tartrate)",
        "meal_timing": "Take with or immediately after a meal (food enhances bioavailability and systemic absorption)",
        "food_interactions": {
            "avoid": ["Alcohol (may precipitate abrupt blood pressure drops and heightened dizziness)"],
            "caution": ["Caffeine and high-energy drinks (stimulants counteract bradycardic rate-control effects)"],
            "beneficial": ["Magnesium-rich foods (pumpkin seeds, almonds, spinach) to support normal cardiac rhythm"]
        },
        "critical_alert": "Never abruptly discontinue beta-blockers without physician supervision (risk of rebound tachycardia and hypertension).",
        "clinical_summary": "Cardioselective beta-1 adrenergic antagonist. Food significantly increases systemic bioavailability of metoprolol tartrate by reducing first-pass hepatic extraction."
    },
    {
        "id": "atenolol",
        "name": "Atenolol",
        "brand_names": ["Tenormin", "Aten", "Betacard"],
        "category": "Cardiovascular (Beta-1 Selective Blocker)",
        "default_dosage": "50 mg",
        "meal_timing": "Take once daily, preferably at the same time, with or without meals",
        "food_interactions": {
            "avoid": ["Excessive alcohol", "High amounts of orange juice consumed at the exact same moment (may mildly decrease absorption)"],
            "caution": ["Do not stop taking abruptly"],
            "beneficial": ["Heart-healthy Mediterranean and DASH foods, omega-3 rich walnuts and chia seeds"]
        },
        "critical_alert": "Do not skip doses. Monitor pulse rate before taking (hold if heart rate < 55 bpm unless cleared).",
        "clinical_summary": "Hydrophilic beta-1 blocker that slows heart rate, decreases myocardial contractility, and lowers blood pressure."
    },
    {
        "id": "furosemide",
        "name": "Furosemide",
        "brand_names": ["Lasix", "Frusenex"],
        "category": "Diuretic (Loop Diuretic)",
        "default_dosage": "20 mg or 40 mg",
        "meal_timing": "Take in the morning with a meal (to avoid sleep disruption from nocturia and minimize stomach irritation)",
        "food_interactions": {
            "avoid": ["Excessive sodium/salty snacks (negates diuretic efficacy)", "Heavy alcohol"],
            "caution": ["Furosemide causes heavy urinary loss of potassium and magnesium; hypokalemia is a frequent complication"],
            "beneficial": [
                "Potassium-rich foods (tender coconut water, bananas, oranges, spinach, potatoes, lentils) to replenish electrolyte losses",
                "Magnesium-rich foods (seeds, whole grains)"
            ]
        },
        "critical_alert": "Depletes bodily potassium and magnesium. Consume potassium-rich natural foods or supplements as advised by your physician.",
        "clinical_summary": "Inhibits Na-K-2Cl symporter in the thick ascending limb of the loop of Henle. Produces potent diuresis with marked excretion of sodium, chloride, potassium, and water."
    },
    {
        "id": "hydrochlorothiazide",
        "name": "Hydrochlorothiazide",
        "brand_names": ["Esidrex", "Aquazide", "Hydrazide"],
        "category": "Diuretic (Thiazide)",
        "default_dosage": "12.5 mg or 25 mg",
        "meal_timing": "Take once daily in the morning with or without food",
        "food_interactions": {
            "avoid": ["High sodium processed foods", "Excessive black licorice (worsens hypokalemia)"],
            "caution": ["Causes mild potassium and magnesium loss; may slightly raise uric acid and blood glucose"],
            "beneficial": ["Potassium-containing fruits, vegetables, and hydrating broths"]
        },
        "critical_alert": "Take in the morning to prevent waking up at night to urinate. Monitor blood electrolytes periodically.",
        "clinical_summary": "Inhibits sodium and chloride reabsorption in the distal convoluted tubules, producing modest diuresis and vasodilation."
    },

    # ------------------ DYSLIPIDEMIA / CHOLESTEROL ------------------
    {
        "id": "atorvastatin",
        "name": "Atorvastatin",
        "brand_names": ["Lipitor", "Atorva", "Storvas", "Tonact", "Atocor"],
        "category": "Lipid-Lowering (HMG-CoA Reductase Inhibitor / Statin)",
        "default_dosage": "10 mg or 20 mg",
        "meal_timing": "Take once daily in the evening or bedtime, with or without food",
        "food_interactions": {
            "avoid": ["Grapefruit, grapefruit juice, and Seville oranges (CYP3A4 inhibition elevates statin blood levels, drastically increasing risk of myopathy and rhabdomyolysis)", "Heavy alcohol (increases hepatic strain)"],
            "caution": ["Do not take huge doses of oat bran or pectin simultaneously; space fiber supplements by 1-2 hours"],
            "beneficial": [
                "Soluble fiber foods (oats, isabgol/psyllium husk, fenugreek, apples, lentils) to synergistically reduce LDL-C",
                "Omega-3 fatty acids (flaxseed, chia, walnuts, fish) and plant sterols"
            ]
        },
        "critical_alert": "Avoid grapefruit and grapefruit juice. Promptly report any unexplained muscle tenderness, weakness, or dark urine.",
        "clinical_summary": "Competitively inhibits HMG-CoA reductase, the rate-limiting enzyme in cholesterol biosynthesis. Grapefruit compounds block CYP3A4-mediated hepatic clearance."
    },
    {
        "id": "rosuvastatin",
        "name": "Rosuvastatin",
        "brand_names": ["Crestor", "Rozavel", "Rosuvas", "Novastat"],
        "category": "Lipid-Lowering (HMG-CoA Reductase Inhibitor / Statin)",
        "default_dosage": "10 mg",
        "meal_timing": "Take once daily at any time of day, with or without food",
        "food_interactions": {
            "avoid": ["Antacids containing aluminum and magnesium hydroxide within 2 hours of dosing (decreases absorption by 50%)", "Excessive alcohol"],
            "caution": ["Less CYP3A4 dependent than atorvastatin, but moderation with grapefruit is still prudent"],
            "beneficial": ["Heart-healthy monounsaturated fats (mustard oil, olive oil), soluble fiber, and antioxidant vegetables"]
        },
        "critical_alert": "Space antacid medications by at least 2 hours. Report unexplained muscle aches or fatigue.",
        "clinical_summary": "Hydrophilic statin cleared primarily by CYP2C9 and biliary excretion. Demonstrates superior LDL-C lowering and HDL elevation efficacy."
    },

    # ------------------ THYROID ------------------
    {
        "id": "levothyroxine",
        "name": "Levothyroxine",
        "brand_names": ["Thyronorm", "Eltroxin", "Synthroid", "Thyrox"],
        "category": "Thyroid Hormone Replacement (T4)",
        "default_dosage": "25 mcg, 50 mcg, or 100 mcg",
        "meal_timing": "STRICT REQUIREMENT: Take first thing in the morning on an EMPTY STOMACH with a full glass of plain water, at least 30 to 60 minutes before breakfast or morning tea/coffee",
        "food_interactions": {
            "avoid": [
                "Taking with milk, tea, coffee, or breakfast (absorption drops by 40-60%)",
                "Soy products (soybean, soy milk, tofu) and walnuts within 4 hours",
                "Calcium-fortified drinks or supplements within 4 hours",
                "Iron supplements (ferrous sulfate) within 4 hours"
            ],
            "caution": ["High dietary fiber meals taken immediately after can trap thyroxine in the intestinal lumen"],
            "beneficial": ["Balanced nutritious meals with adequate selenium (mushrooms, sunflower seeds) and zinc after waiting 60 minutes post-dose"]
        },
        "critical_alert": "Must be taken on an empty stomach with plain water. Keep a minimum 4-hour gap between Levothyroxine and Calcium, Iron, Soy, or Dairy supplements.",
        "clinical_summary": "Synthetic crystalline L-tetraiodothyronine (T4). Bioavailability is heavily compromised by gastric pH alterations, divalent cations (Ca2+, Fe2+), caffeine, and dietary fibers."
    },

    # ------------------ GASTROINTESTINAL & ACIDITY ------------------
    {
        "id": "pantoprazole",
        "name": "Pantoprazole",
        "brand_names": ["Pan-40", "Pantocid", "Protium", "Pantodac"],
        "category": "Gastrointestinal (Proton Pump Inhibitor - PPI)",
        "default_dosage": "40 mg",
        "meal_timing": "Take 30 to 60 minutes BEFORE the morning meal (breakfast) on an empty stomach",
        "food_interactions": {
            "avoid": ["Spicy, excessively greasy/fried foods, carbonated sodas, and late-night heavy meals that trigger acid reflux", "Alcohol"],
            "caution": ["Long-term PPI use (>1 year) can reduce absorption of dietary Vitamin B12, Calcium, and Magnesium"],
            "beneficial": [
                "Soothing gut-friendly foods (plain yogurt/curd, coconut water, boiled oats, bananas, bottle gourd)",
                "Foods rich in magnesium and calcium once meals resume"
            ]
        },
        "critical_alert": "Must be swallowed whole 30-60 minutes before food so that drug peak coincides with activation of proton pumps by the meal.",
        "clinical_summary": "Irreversibly binds the H+/K+ ATPase pump in gastric parietal cells. Food stimulates pump translocation, hence timing before food is critical for optimal acid suppression."
    },
    {
        "id": "omeprazole",
        "name": "Omeprazole",
        "brand_names": ["Omez", "Prilosec", "Ocid", "Lokit"],
        "category": "Gastrointestinal (Proton Pump Inhibitor - PPI)",
        "default_dosage": "20 mg",
        "meal_timing": "Take once daily in the morning 30-60 minutes before breakfast",
        "food_interactions": {
            "avoid": ["Trigger foods: citrus juices, tomatoes, caffeine, chocolates, deep-fried snacks"],
            "caution": ["Do not open or crush enteric-coated capsules"],
            "beneficial": ["Non-acidic vegetables, rice porridge, stewed apples, chamomile or fennel tea"]
        },
        "critical_alert": "Take before your morning meal. Swallow whole with a glass of water.",
        "clinical_summary": "Potent inhibitor of basal and stimulated gastric acid secretion. Requires acidic gastric activation followed by covalent canalicular pump binding."
    },

    # ------------------ ANTIPLATELETS & ANTICOAGULANTS ------------------
    {
        "id": "aspirin",
        "name": "Aspirin (Low Dose)",
        "brand_names": ["Ecosprin", "Disprin", "Bayer Aspirin", "Delisprin"],
        "category": "Antiplatelet / Cardiovascular",
        "default_dosage": "75 mg or 150 mg",
        "meal_timing": "Take WITH or immediately AFTER a meal with a full glass of water (never on an empty stomach)",
        "food_interactions": {
            "avoid": [
                "Alcohol (significantly compounds gastric irritation and risk of severe upper gastrointestinal bleeding)",
                "Massive megadoses of garlic, ginger, ginkgo biloba, or omega-3 fish oil supplements that compound antiplatelet activity"
            ],
            "caution": ["Taking on an empty stomach frequently induces erosive gastritis and gastric mucosal ulceration"],
            "beneficial": ["Milk, curd, or a warm whole-grain meal before taking to coat the gastric mucosa"]
        },
        "critical_alert": "Always take with or after meals to protect your stomach lining. Do NOT consume alcohol with Aspirin.",
        "clinical_summary": "Irreversibly acetylates COX-1 in platelets, preventing thromboxane A2 synthesis. Direct mucosal contact and systemic PG inhibition can precipitate gastric mucosal injury without food."
    },
    {
        "id": "clopidogrel",
        "name": "Clopidogrel",
        "brand_names": ["Plavix", "Deplatt", "Clopilet", "Ceruvit"],
        "category": "Antiplatelet (P2Y12 Inhibitor)",
        "default_dosage": "75 mg",
        "meal_timing": "Take once daily with or without food at the same time every day",
        "food_interactions": {
            "avoid": ["Excessive alcohol", "Concomitant high doses of natural anticoagulants (vitamin E megadoses, high-dose feverfew)"],
            "caution": ["Avoid taking with Omeprazole concurrently unless prescribed, as Omeprazole inhibits CYP2C19 activation of Clopidogrel (Pantoprazole is preferred)"],
            "beneficial": ["Balanced diet with antioxidant vegetables and moderate healthy fats"]
        },
        "critical_alert": "Check with doctor before taking over-the-counter pain medications or herbal blood thinners.",
        "clinical_summary": "Thienopyridine prodrug bioactivated by CYP2C19 to inhibit ADP-induced platelet aggregation. Less gastrotoxic than aspirin, can be taken with or without food."
    },
    {
        "id": "warfarin",
        "name": "Warfarin",
        "brand_names": ["Coumadin", "Uniwarfin", "Warf"],
        "category": "Anticoagulant (Vitamin K Antagonist)",
        "default_dosage": "2 mg, 3 mg, or 5 mg (as titrated by INR)",
        "meal_timing": "Take once daily in the evening, with or without food, at the exact same hour",
        "food_interactions": {
            "avoid": [
                "Cranberry juice, pomegranate juice, and alcohol (can elevate INR dangerously)",
                "Drastic sudden swings in dietary Vitamin K intake"
            ],
            "caution": [
                "Do NOT suddenly start or stop eating large quantities of Vitamin K rich foods (spinach, kale, methi leaves, broccoli, cabbage). Keep your daily intake CONSISTENT"
            ],
            "beneficial": ["Consistent, steady daily portions of green vegetables rather than extreme fluctuations"]
        },
        "critical_alert": "CRITICAL FOOD INTERACTION: Vitamin K directly opposes Warfarin. Keep your intake of green leafy vegetables steady from day to day.",
        "clinical_summary": "Inhibits vitamin K epoxide reductase complex 1 (VKORC1), stopping gamma-carboxylation of clotting factors II, VII, IX, and X. Large fluctuations in dietary vitamin K destabilize anticoagulation."
    },

    # ------------------ RESPIRATORY & ANTIHISTAMINES ------------------
    {
        "id": "montelukast",
        "name": "Montelukast",
        "brand_names": ["Singulair", "Montair", "Montek", "Telekast"],
        "category": "Respiratory / Anti-asthmatic (Leukotriene Receptor Antagonist)",
        "default_dosage": "10 mg",
        "meal_timing": "Take once daily in the evening, with or without food",
        "food_interactions": {
            "avoid": ["Alcohol (may increase drowsiness and sedation)"],
            "caution": ["None significant with general food"],
            "beneficial": ["Anti-inflammatory foods (turmeric/curcumin, ginger, warm soups, honey) to support bronchial health"]
        },
        "critical_alert": "Best taken in the evening to protect against nocturnal asthma and morning allergic rhinitis symptoms.",
        "clinical_summary": "Selective antagonist of cysteinyl leukotriene CysLT1 receptor. Inhibits bronchoconstriction, mucosal edema, and cellular inflammation."
    },
    {
        "id": "cetirizine",
        "name": "Cetirizine",
        "brand_names": ["Cetzine", "Zyrtec", "Alerid", "Okacet"],
        "category": "Antihistamine (Second Generation H1 Blocker)",
        "default_dosage": "10 mg",
        "meal_timing": "Take in the evening or bedtime with or without food",
        "food_interactions": {
            "avoid": ["Alcohol and CNS depressants (causes severe drowsiness and impaired reflexes)"],
            "caution": ["Food slightly delays time to peak concentration (Tmax) but does not decrease total absorption"],
            "beneficial": ["Warm herbal teas (tulsi, ginger, peppermint) to soothe airway passages"]
        },
        "critical_alert": "Avoid driving or operating machinery if you experience drowsiness. Do not drink alcohol.",
        "clinical_summary": "Second-generation peripheral H1 receptor antagonist with minimal blood-brain barrier penetration, providing effective allergy relief with reduced central sedation."
    },

    # ------------------ ANTIBIOTICS ------------------
    {
        "id": "amoxicillin_clavulanate",
        "name": "Amoxicillin and Potassium Clavulanate",
        "brand_names": ["Augmentin", "Moxikind-CV", "Clavam", "Mega-CV"],
        "category": "Antibiotic (Penicillin / Beta-lactamase inhibitor)",
        "default_dosage": "625 mg",
        "meal_timing": "Take at the START of a meal or with food",
        "food_interactions": {
            "avoid": ["Alcohol during antibiotic therapy", "Skipping doses or stopping before full course is finished"],
            "caution": ["Clavulanic acid can cause diarrhea and nausea if taken on an empty stomach"],
            "beneficial": [
                "Probiotic foods (fresh homemade curd/yogurt, buttermilk) taken 2 hours apart from the antibiotic to replenish healthy gut microbiota",
                "Hydrating fluids and easily digestible meals (khichdi, vegetable soup)"
            ]
        },
        "critical_alert": "Take at the start of a meal to enhance absorption of clavulanate and prevent nausea and diarrhea. Complete full course.",
        "clinical_summary": "Co-administration with food enhances clavulanate absorption and optimizes gastrointestinal tolerability while amoxicillin bactericidal cell wall synthesis inhibition proceeds."
    },
    {
        "id": "ciprofloxacin",
        "name": "Ciprofloxacin",
        "brand_names": ["Cifran", "Cipro", "Ciplox"],
        "category": "Antibiotic (Fluoroquinolone)",
        "default_dosage": "500 mg",
        "meal_timing": "Take 2 hours before or 2 hours AFTER dairy products or mineral-rich meals",
        "food_interactions": {
            "avoid": [
                "Taking directly with milk, yogurt, paneer, cheese, or calcium-fortified juices (calcium chelates the drug, reducing absorption by up to 90%)",
                "Iron, zinc, or magnesium antacids/supplements taken simultaneously"
            ],
            "caution": ["Caffeine (ciprofloxacin inhibits caffeine clearance, potentially causing tremors, palpitations, and insomnia)"],
            "beneficial": ["Plenty of water throughout the day to prevent crystalluria"]
        },
        "critical_alert": "DO NOT take with dairy products (milk, yogurt) or calcium/iron supplements. Keep a 2-hour window before and after.",
        "clinical_summary": "Polyvalent cations (Ca2+, Mg2+, Fe2+, Al3+) form insoluble coordination chelates with the 4-keto and 3-carboxyl groups of fluoroquinolones, preventing intestinal absorption."
    },
    {
        "id": "azithromycin",
        "name": "Azithromycin",
        "brand_names": ["Azithral", "Zithromax", "Azee", "Azimax"],
        "category": "Antibiotic (Macrolide / Azalide)",
        "default_dosage": "500 mg",
        "meal_timing": "May be taken with or without food; taking with a light meal reduces stomach discomfort",
        "food_interactions": {
            "avoid": ["Aluminum and magnesium antacids taken at the exact same time (reduces peak concentration)"],
            "caution": ["Avoid heavy greasy meals which may worsen nausea"],
            "beneficial": ["Yogurt/buttermilk spaced 2 hours apart to safeguard beneficial gut microflora"]
        },
        "critical_alert": "Take once daily at the same time. Complete full prescribed course (usually 3 to 5 days).",
        "clinical_summary": "Reversibly binds the 50S ribosomal subunit of susceptible microorganisms. Tablets have high oral bioavailability and tissue penetration."
    },

    # ------------------ ANALGESICS & ANTI-INFLAMMATORY ------------------
    {
        "id": "paracetamol",
        "name": "Paracetamol (Acetaminophen)",
        "brand_names": ["Dolo 650", "Calpol", "Crocin", "Tylenol", "Pacimol"],
        "category": "Analgesic & Antipyretic",
        "default_dosage": "650 mg",
        "meal_timing": "Can be taken with or without food (taking on an empty stomach acts faster; taking with food is gentler)",
        "food_interactions": {
            "avoid": ["Alcohol (severely elevates risk of acute toxic hepatic necrosis / liver injury)"],
            "caution": ["Do not exceed maximum daily limit of 4000 mg (or 3000 mg in chronic use) across all combination products"],
            "beneficial": ["Warm hydration, light broths, electrolyte fluids, herbal teas"]
        },
        "critical_alert": "DO NOT drink alcohol while taking Paracetamol. Chronic alcohol consumption drastically increases liver toxicity risk.",
        "clinical_summary": "Acts primarily on central prostaglandin synthesis with minimal peripheral anti-inflammatory action. Concomitant ethanol induces CYP2E1, shunting metabolism into toxic NAPQI."
    },
    {
        "id": "ibuprofen",
        "name": "Ibuprofen",
        "brand_names": ["Brufen", "Advil", "Motrin", "Ibugesic"],
        "category": "NSAID (Nonsteroidal Anti-inflammatory Drug)",
        "default_dosage": "400 mg",
        "meal_timing": "STRICTLY take WITH food, milk, or a meal (never on an empty stomach)",
        "food_interactions": {
            "avoid": ["Alcohol (exponentially increases risk of stomach ulcers and GI bleeding)"],
            "caution": ["Excess sodium intake; NSAIDs can promote fluid retention and blunted BP control"],
            "beneficial": ["Warm milk, oats porridge, or a cooked meal before dose to coat gastric mucosa"]
        },
        "critical_alert": "Always take after food or with milk to protect your stomach lining from ulcers and erosions.",
        "clinical_summary": "Non-selective COX inhibitor. Depletes gastroprotective prostaglandins (PGE2, PGI2) in gastric mucosa. Food reduces peak contact irritation."
    },

    # ------------------ SUPPLEMENTS & MINERALS ------------------
    {
        "id": "calcium_vitamin_d3",
        "name": "Calcium Carbonate + Vitamin D3",
        "brand_names": ["Shelcal", "Calcirol", "Cipcal", "Ostocalcium"],
        "category": "Mineral & Vitamin Supplement",
        "default_dosage": "500 mg Calcium + 250/500 IU D3",
        "meal_timing": "Take WITH meals (gastric acid produced during meals is essential to dissolve and absorb calcium carbonate)",
        "food_interactions": {
            "avoid": [
                "Taking simultaneously with Levothyroxine, Ciprofloxacin, or Iron (space by at least 2 to 4 hours)",
                "Excessive caffeine or carbonated cola beverages (increases urinary calcium excretion)"
            ],
            "caution": ["High-oxalate foods (spinach, beet greens) eaten simultaneously can bind a portion of calcium, though overall diet is healthy"],
            "beneficial": ["Dairy products, fortified milk, sesame seeds (til), and sunlight exposure for natural vitamin D activation"]
        },
        "critical_alert": "Calcium carbonate REQUIRES stomach acid; take with meals. Keep a 4-hour gap from Levothyroxine and Iron supplements.",
        "clinical_summary": "Calcium carbonate requires acidic ionization for intestinal absorption via TRPV6 channels. Divalent Ca2+ binds thyroxine and fluoroquinolones into unabsorbable complexes."
    },
    {
        "id": "ferrous_ascorbate",
        "name": "Ferrous Ascorbate / Iron Supplement",
        "brand_names": ["Orofer-XT", "Fefol", "Irospan", "Autrin"],
        "category": "Hematinic / Iron Supplement",
        "default_dosage": "100 mg elemental iron",
        "meal_timing": "Best taken on an empty stomach with a Vitamin C source (lemon water or amla juice) for maximum absorption, OR with a light snack if nausea occurs",
        "food_interactions": {
            "avoid": [
                "Tea, coffee, green tea (tannins and polyphenols inhibit iron absorption by up to 75%)",
                "Milk, cheese, yogurt, and calcium tablets (calcium competes directly for the DMT1 transporter) - space by 2 hours",
                "High-phytate unfermented bran taken in the exact same mouthful"
            ],
            "caution": ["Stools may turn dark green/black (harmless)"],
            "beneficial": [
                "Vitamin C foods (Indian gooseberry/amla, lemon, guava, sweet lime, capsicum) taken alongside iron drastically enhance bioavailability"
            ]
        },
        "critical_alert": "Do NOT take iron with tea, coffee, milk, or calcium tablets. Pair with lemon water or amla for superior absorption.",
        "clinical_summary": "Ascorbate maintains iron in the soluble ferrous (Fe2+) state, facilitating uptake via divalent metal transporter 1 (DMT1). Tannins, polyphenols, and calcium strongly inhibit uptake."
    }
]

def generate():
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "medicines_data.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(MEDICINES_DATA, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {len(MEDICINES_DATA)} curated medicines in {out_file}")

if __name__ == "__main__":
    generate()
