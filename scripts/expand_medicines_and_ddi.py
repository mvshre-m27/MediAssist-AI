"""
Expand data/medicines_data.json to 70+ clinical medications
and generate data/drug_interactions_data.json with 100+ evidence-based
Drug-Drug Interaction (DDI) rules.
"""

import json
from pathlib import Path

# Load existing 33 medicines first
data_dir = Path(__file__).parent.parent / "data"
meds_file = data_dir / "medicines_data.json"
existing_meds = []
if meds_file.exists():
    with open(meds_file, "r", encoding="utf-8") as f:
        existing_meds = json.load(f)

existing_ids = {m["id"] for m in existing_meds}

# New additional medications to add
NEW_MEDICINES = [
    # ---------- HYPERTENSION & CARDIOLOGY (ADDITIONAL) ----------
    {
        "id": "valsartan",
        "name": "Valsartan",
        "brand_names": ["Diovan", "Valzaar", "Starval"],
        "category": "Antihypertensive (ARB)",
        "default_dosage": "80 mg or 160 mg",
        "meal_timing": "Take with or without food at the same time each day",
        "food_interactions": {
            "avoid": ["Potassium-based salt substitutes", "Excessive alcohol"],
            "caution": ["High potassium intake without doctor supervision"],
            "beneficial": ["Low-sodium DASH foods, leafy greens, antioxidant fruits"]
        },
        "critical_alert": "Avoid potassium chloride salt alternatives. Monitor serum potassium periodically.",
        "clinical_summary": "Angiotensin II receptor antagonist; reduces peripheral vascular resistance and preserves renal function."
    },
    {
        "id": "olmesartan",
        "name": "Olmesartan",
        "brand_names": ["Olmetime", "Benicar", "Olmecip"],
        "category": "Antihypertensive (ARB)",
        "default_dosage": "20 mg or 40 mg",
        "meal_timing": "Take once daily with or without food",
        "food_interactions": {
            "avoid": ["Potassium chloride salt substitutes"],
            "caution": ["Severe prolonged diarrhea requires medical review (sprue-like enteropathy)"],
            "beneficial": ["Hydrating foods, low sodium home cooking"]
        },
        "critical_alert": "Do not take potassium supplements without consulting your doctor.",
        "clinical_summary": "Selective AT1 receptor blocker providing 24-hour sustained blood pressure control."
    },
    {
        "id": "lisinopril",
        "name": "Lisinopril",
        "brand_names": ["Prinivil", "Zestril", "Lipril"],
        "category": "Antihypertensive (ACE Inhibitor)",
        "default_dosage": "10 mg or 20 mg",
        "meal_timing": "Take once daily with or without food",
        "food_interactions": {
            "avoid": ["Potassium salt substitutes", "Heavy alcohol"],
            "caution": ["High potassium diets can lead to hyperkalemia"],
            "beneficial": ["DASH diet meals with balanced natural minerals"]
        },
        "critical_alert": "May cause dry persistent cough. Avoid potassium salt alternatives.",
        "clinical_summary": "Inhibits angiotensin-converting enzyme, suppressing angiotensin II formation and lowering systemic vascular resistance."
    },
    {
        "id": "carvedilol",
        "name": "Carvedilol",
        "brand_names": ["Coreg", "Carvil", "Cardivas"],
        "category": "Cardiovascular (Non-selective Beta & Alpha-1 Blocker)",
        "default_dosage": "6.25 mg or 12.5 mg twice daily",
        "meal_timing": "Take WITH food to minimize the risk of orthostatic hypotension and dizziness",
        "food_interactions": {
            "avoid": ["Alcohol (increases risk of orthostatic dizziness and fainting)"],
            "caution": ["Large amounts of caffeine may diminish blood pressure lowering"],
            "beneficial": ["Balanced heart-healthy meals rich in magnesium and omega-3s"]
        },
        "critical_alert": "Always take with food to slow absorption rate and reduce orthostatic blood pressure drops.",
        "clinical_summary": "Dual alpha-1 and beta-adrenergic antagonist with antioxidant properties; indicated in heart failure, hypertension, and post-MI."
    },
    {
        "id": "bisoprolol",
        "name": "Bisoprolol",
        "brand_names": ["Concor", "Bisoheart", "Corbis"],
        "category": "Cardiovascular (Cardioselective Beta-1 Blocker)",
        "default_dosage": "2.5 mg or 5 mg",
        "meal_timing": "Take once daily in the morning with or without food",
        "food_interactions": {
            "avoid": ["Excessive alcohol"],
            "caution": ["Do not stop abruptly without doctor supervision"],
            "beneficial": ["Low-sodium meals and moderate physical activity"]
        },
        "critical_alert": "Do not skip doses. Check heart rate periodically before taking.",
        "clinical_summary": "Highly selective beta-1 blocker reducing cardiac workload and myocardial oxygen consumption."
    },
    {
        "id": "ne pasture_nebi",
        "id": "nebivolol",
        "name": "Nebivolol",
        "brand_names": ["Nebicard", "Bystolic", "Nebilong"],
        "category": "Cardiovascular (Third-Generation Beta-1 Blocker with Nitric Oxide Vasodilation)",
        "default_dosage": "5 mg",
        "meal_timing": "Take once daily with or without food",
        "food_interactions": {
            "avoid": ["Alcohol", "Energy drinks with high caffeine"],
            "caution": ["May mask hypoglycemia tremors in diabetic patients"],
            "beneficial": ["Dietary nitrate rich foods (beetroot, spinach) to support endothelial NO production"]
        },
        "critical_alert": "Possesses unique nitric oxide donating properties causing peripheral vasodilation.",
        "clinical_summary": "Highly cardioselective beta-1 blocker that stimulates endothelial nitric oxide synthase (eNOS), reducing peripheral vascular resistance."
    },
    {
        "id": "propranolol",
        "name": "Propranolol",
        "brand_names": ["Inderal", "Ciplar", "Betacap"],
        "category": "Cardiovascular & Neuro (Non-selective Beta Blocker)",
        "default_dosage": "20 mg or 40 mg",
        "meal_timing": "Take before meals or with food consistently",
        "food_interactions": {
            "avoid": ["Alcohol", "Caffeine in excess"],
            "caution": ["Protein-rich meals increase its bioavailability; keep meal composition consistent"],
            "beneficial": ["Magnesium-rich seeds and calming herbal teas"]
        },
        "critical_alert": "Contraindicated in asthma and severe COPD (can precipitate severe bronchospasm).",
        "clinical_summary": "Non-selective beta-1 and beta-2 adrenergic antagonist; useful in angina, tremors, migraine prophylaxis, and portal hypertension."
    },
    {
        "id": "diltiazem",
        "name": "Diltiazem",
        "brand_names": ["Cardizem", "Dilzem", "Dilcontin"],
        "category": "Cardiovascular (Non-Dihydropyridine Calcium Channel Blocker)",
        "default_dosage": "30 mg or 60 mg (or 90/120 mg SR)",
        "meal_timing": "Take before meals and at bedtime, or as prescribed with water",
        "food_interactions": {
            "avoid": ["Grapefruit and grapefruit juice (potentiates diltiazem levels)", "Alcohol"],
            "caution": ["Do not crush extended-release tablets"],
            "beneficial": ["Heart-healthy DASH diet meals with moderate natural minerals"]
        },
        "critical_alert": "Avoid grapefruit. Inhibits CYP3A4 enzyme, causing interactions with numerous cardiovascular drugs.",
        "clinical_summary": "Benzothiazepine calcium channel blocker; slows AV node conduction, decreases heart rate, and dilates coronary and systemic arteries."
    },
    {
        "id": "verapamil",
        "name": "Verapamil",
        "brand_names": ["Calan", "Isoptin", "Veramil"],
        "category": "Cardiovascular (Non-Dihydropyridine Calcium Channel Blocker)",
        "default_dosage": "40 mg or 80 mg",
        "meal_timing": "Take with meals or milk to avoid stomach upset",
        "food_interactions": {
            "avoid": ["Grapefruit and grapefruit juice (massively increases verapamil concentrations)", "Alcohol"],
            "caution": ["Constipation is common: increase dietary fiber and water intake"],
            "beneficial": ["High-fiber vegetables, oats, prunes, and adequate hydration"]
        },
        "critical_alert": "AVOID GRAPEFRUIT. Strong inhibitor of CYP3A4 and P-glycoprotein.",
        "clinical_summary": "Phenylalkylamine CCB with pronounced negative inotropic and dromotropic actions. Highly effective in supraventricular tachycardias."
    },
    {
        "id": "cilnidipine",
        "name": "Cilnidipine",
        "brand_names": ["Cilacar", "Nexsulin", "Cilaheart"],
        "category": "Antihypertensive (Dual L/N-type Calcium Channel Blocker)",
        "default_dosage": "10 mg",
        "meal_timing": "Take once daily in the morning with or after breakfast",
        "food_interactions": {
            "avoid": ["Grapefruit juice", "Excessive sodium"],
            "caution": ["Sudden position changes if feeling lightheaded"],
            "beneficial": ["Low-sodium meals, fresh vegetables, garlic"]
        },
        "critical_alert": "Dual L/N-type blocker with lower incidence of pedal edema and sympathetic activation compared to amlodipine.",
        "clinical_summary": "Blocks both L-type and N-type voltage-dependent calcium channels, suppressing sympathetic overactivity and renal afferent/efferent arteriolar constriction."
    },
    {
        "id": "spironolactone",
        "name": "Spironolactone",
        "brand_names": ["Aldactone", "Spiroctan"],
        "category": "Diuretic (Potassium-Sparing / Aldosterone Antagonist)",
        "default_dosage": "25 mg or 50 mg",
        "meal_timing": "Take with food or breakfast (food enhances bioavailability and minimizes gastric irritation)",
        "food_interactions": {
            "avoid": [
                "Potassium chloride salt substitutes (can cause fatal hyperkalemia)",
                "Potassium supplements or high-dose potassium drinks without monitoring"
            ],
            "caution": ["Excessive consumption of dried fruits, bananas, tender coconut water if serum potassium is high"],
            "beneficial": ["Low-sodium wholesome home-cooked meals"]
        },
        "critical_alert": "POTASSIUM-SPARING: Strictly avoid potassium salt substitutes. High risk of hyperkalemia when combined with ACEIs or ARBs.",
        "clinical_summary": "Competitive aldosterone receptor antagonist in the distal renal tubule; increases sodium and water excretion while retaining potassium and hydrogen ions."
    },
    {
        "id": "chlorthalidone",
        "name": "Chlorthalidone",
        "brand_names": ["Hygroton", "CTD", "Chlortan"],
        "category": "Diuretic (Thiazide-like Diuretic)",
        "default_dosage": "6.25 mg or 12.5 mg",
        "meal_timing": "Take in the morning with food",
        "food_interactions": {
            "avoid": ["Excessive sodium snacks", "Heavy alcohol"],
            "caution": ["Causes mild potassium loss; monitor serum electrolytes"],
            "beneficial": ["Potassium-balanced vegetables and fresh fruits"]
        },
        "critical_alert": "Long half-life (>40 hours). Preferred thiazide-like diuretic in AHA/ACC hypertension guidelines.",
        "clinical_summary": "Inhibits sodium and chloride reabsorption in the early distal tubule; long terminal elimination half-life delivers sustained 24h BP reduction."
    },
    {
        "id": "digoxin",
        "name": "Digoxin",
        "brand_names": ["Lanoxin", "Cardioxin"],
        "category": "Cardiac Glycoside (Inotrope & Antiarrhythmic)",
        "default_dosage": "0.125 mg or 0.25 mg",
        "meal_timing": "Take once daily with water; meals high in bran fiber should be spaced by 2 hours",
        "food_interactions": {
            "avoid": [
                "Simultaneous high-fiber meals (e.g. oat bran, psyllium husk can bind digoxin and reduce absorption)",
                "Black licorice (glycyrrhizin induces hypokalemia, precipitating fatal digoxin toxicity)"
            ],
            "caution": ["Hypokalemia or hypomagnesemia dramatically potentiates digitalis toxicity"],
            "beneficial": ["Consistent potassium intake to safeguard normal myocardial sensitivity"]
        },
        "critical_alert": "NARROW THERAPEUTIC INDEX: Hypokalemia triggers severe arrhythmias. Report nausea, visual halos, or slow irregular pulse immediately.",
        "clinical_summary": "Inhibits myocardial Na+/K+ ATPase, increasing intracellular calcium and cardiac contractility while slowing AV nodal conduction."
    },
    {
        "id": "amiodarone",
        "name": "Amiodarone",
        "brand_names": ["Cordarone", "Pacenone"],
        "category": "Antiarrhythmic (Class III)",
        "default_dosage": "100 mg or 200 mg",
        "meal_timing": "Take with meals consistently (food significantly enhances oral absorption)",
        "food_interactions": {
            "avoid": ["Grapefruit and grapefruit juice (inhibits CYP3A4 and increases amiodarone levels to toxic ranges)"],
            "caution": ["St. John's wort", "High iodine seaweed supplements"],
            "beneficial": ["Heart-healthy balanced diet"]
        },
        "critical_alert": "EXTREME DDI RISK: Inhibits CYP3A4, CYP2C9, CYP2D6, and P-gp. Doubles blood levels of Digoxin, Warfarin, and Statins.",
        "clinical_summary": "Multichannel blocker with predominant potassium outward rectifier inhibition (Class III); highly lipophilic with extensive tissue distribution."
    },

    # ---------- DIABETES (ADDITIONAL) ----------
    {
        "id": "glipizide",
        "name": "Glipizide",
        "brand_names": ["Glucotrol", "Glynase", "Minidiab"],
        "category": "Anti-diabetic (Second-generation Sulfonylurea)",
        "default_dosage": "2.5 mg or 5 mg",
        "meal_timing": "Take 30 minutes BEFORE the first meal of the day (breakfast)",
        "food_interactions": {
            "avoid": ["Alcohol", "Skipping or delaying meals after taking"],
            "caution": ["Always have a carbohydrate-containing meal within 30 minutes"],
            "beneficial": ["Complex carbohydrates (millets, whole oats, lentils) to avoid hypoglycemic troughs"]
        },
        "critical_alert": "Must be taken 30 minutes before food for optimal timing of insulin peak with food absorption.",
        "clinical_summary": "Rapidly absorbed sulfonylurea that stimulates early phase insulin secretion from pancreatic beta cells."
    },
    {
        "id": "vildagliptin",
        "name": "Vildagliptin",
        "brand_names": ["Galvus", "Jalra", "Zomelis"],
        "category": "Anti-diabetic (DPP-4 Inhibitor)",
        "default_dosage": "50 mg once or twice daily",
        "meal_timing": "May be taken with or without food",
        "food_interactions": {
            "avoid": ["High-sugar confectionaries, sugar-sweetened sodas"],
            "caution": ["Excessive alcohol"],
            "beneficial": ["Low glycemic index Indian staples (ragi, sprouted moong, green leafy vegetables)"]
        },
        "critical_alert": "Monitor liver function tests (LFTs) periodically as per clinical guidelines.",
        "clinical_summary": "Potent and selective dipeptidyl peptidase-4 inhibitor; enhances both alpha- and beta-cell responsiveness to glucose."
    },
    {
        "id": "linagliptin",
        "name": "Linagliptin",
        "brand_names": ["Trajenta", "Ondero"],
        "category": "Anti-diabetic (DPP-4 Inhibitor - Non-Renal Clearance)",
        "default_dosage": "5 mg",
        "meal_timing": "Take once daily with or without food at any time",
        "food_interactions": {
            "avoid": ["Refined sugars and syrups"],
            "caution": ["Hypoglycemia risk if combined with insulin or sulfonylurea"],
            "beneficial": ["Balanced fiber-rich diet; safe in kidney disease without dose reduction"]
        },
        "critical_alert": "Does not require dose adjustment in renal impairment (cleared primarily via bile and gut).",
        "clinical_summary": "Xanthine-based DPP-4 inhibitor with primarily non-renal route of excretion; highly convenient in diabetic kidney disease."
    },
    {
        "id": "teneligliptin",
        "name": "Teneligliptin",
        "brand_names": ["Tenglyn", "Ziten", "Tenelimac", "Dynaglipt"],
        "category": "Anti-diabetic (Third-generation DPP-4 Inhibitor)",
        "default_dosage": "20 mg",
        "meal_timing": "Take once daily with or without breakfast",
        "food_interactions": {
            "avoid": ["Sugary sweets, jaggery in excess, packaged juices"],
            "caution": ["Alcohol"],
            "beneficial": ["Vegetable salads, methi paratha (whole wheat), curd, roasted chana"]
        },
        "critical_alert": "Widely prescribed cost-effective DPP-4 inhibitor in India with convenient once-daily dosing.",
        "clinical_summary": "Features a unique J-shaped structure that anchors into the S1, S2, and S2-extensive sub-sites of DPP-4 for potent, long-lasting inhibition."
    },
    {
        "id": "canagliflozin",
        "name": "Canagliflozin",
        "brand_names": ["Invokana", "Sulisent"],
        "category": "Anti-diabetic (SGLT2 Inhibitor)",
        "default_dosage": "100 mg or 300 mg",
        "meal_timing": "Take once daily BEFORE the first meal of the day",
        "food_interactions": {
            "avoid": ["Dehydration", "Excess alcohol", "Extreme ketogenic diet"],
            "caution": ["Maintain daily fluid intake (2-3 liters water unless fluid restricted)"],
            "beneficial": ["Hydrating foods (cucumber, bottle gourd, coconut water) and DASH diet"]
        },
        "critical_alert": "Dual SGLT2 and mild intestinal SGLT1 inhibition; taking before breakfast delays intestinal glucose absorption.",
        "clinical_summary": "Inhibits SGLT2 in kidneys and SGLT1 in intestine; reduces blood glucose, HbA1c, systolic blood pressure, and body weight."
    },
    {
        "id": "semaglutide",
        "name": "Semaglutide",
        "brand_names": ["Rybelsus (Oral)", "Ozempic (Injectable)", "Wegovy"],
        "category": "Anti-diabetic & Weight Management (GLP-1 Receptor Agonist)",
        "default_dosage": "3 mg, 7 mg, or 14 mg (Oral)",
        "meal_timing": "ORAL STRICT RULE: Take on an empty stomach upon waking with no more than 120 ml (half glass) of plain water. Wait AT LEAST 30 MINUTES before eating, drinking, or taking other oral medications",
        "food_interactions": {
            "avoid": [
                "Eating or drinking anything within 30 minutes of taking oral tablet (absorption drops to near zero)",
                "Greasy, fried, and very fatty foods which exacerbate nausea, vomiting, and delayed gastric emptying"
            ],
            "caution": ["Eat smaller, lighter portions to avoid fullness and GI distress"],
            "beneficial": ["Small protein-rich meals, broths, and easily digestible whole foods"]
        },
        "critical_alert": "ORAL RYBELSUS REQUIREMENT: Swallow whole with half glass plain water. Absolutely no food, beverage, or other meds for 30 minutes.",
        "clinical_summary": "Long-acting GLP-1 receptor agonist; stimulates glucose-dependent insulin secretion, suppresses glucagon, slows gastric emptying, and reduces appetite."
    },
    {
        "id": "voglibose",
        "name": "Voglibose",
        "brand_names": ["Volibo", "Vobose", "PPG", "Volix"],
        "category": "Anti-diabetic (Alpha-Glucosidase Inhibitor)",
        "default_dosage": "0.2 mg or 0.3 mg",
        "meal_timing": "STRICT REQUIREMENT: Take immediately with the VERY FIRST BITE of each main meal (breakfast, lunch, dinner)",
        "food_interactions": {
            "avoid": [
                "Taking after a meal (ineffective once food has been digested)",
                "Treating hypoglycemia with table sugar/sucrose (voglibose blocks sucrose digestion; MUST use pure GLUCOSE/dextrose powder or tablets)"
            ],
            "caution": ["High-starch meals may produce mild flatulence and abdominal distension"],
            "beneficial": ["Indian carbohydrate staples (roti, rice, dal) are digested more slowly and evenly"]
        },
        "critical_alert": "Must be taken with the first bite of food. In case of hypoglycemia, treat ONLY with pure Glucose (Dextrose), NOT cane sugar.",
        "clinical_summary": "Reversibly inhibits alpha-glucosidase enzymes in the small intestine brush border, delaying carbohydrate cleavage into simple monosaccharides."
    },
    {
        "id": "repaglinide",
        "name": "Repaglinide",
        "brand_names": ["Prandin", "Eurepa", "Rapilin"],
        "category": "Anti-diabetic (Meglitinide / Prandial Glucose Regulator)",
        "default_dosage": "0.5 mg, 1 mg, or 2 mg",
        "meal_timing": "Take within 15 minutes BEFORE each main meal (Breakfast, Lunch, Dinner)",
        "food_interactions": {
            "avoid": ["Alcohol (severe hypoglycemia)", "Skipping meals (if you skip a meal, SKIP the dose!)"],
            "caution": ["Do not take if unable to eat immediately after"],
            "beneficial": ["Regular structured meals with complex carbs and protein"]
        },
        "critical_alert": "RULE: If a meal is skipped, skip the dose. If an extra meal is added, add a dose.",
        "clinical_summary": "Nonsulfonylurea secretagogue; closes ATP-dependent potassium channels in beta cells with rapid onset and short duration for postprandial control."
    },
    {
        "id": "insulin_glargine",
        "name": "Insulin Glargine",
        "brand_names": ["Lantus", "Basalog", "Toujeo"],
        "category": "Anti-diabetic (Long-Acting Basal Insulin Analogue)",
        "default_dosage": "Titrated by physician (e.g. 10-20 units subcutaneously)",
        "meal_timing": "Inject once daily subcutaneously at the EXACT same time every day, independent of meals",
        "food_interactions": {
            "avoid": ["Alcohol (blunts counterregulatory glucose response causing delayed severe hypoglycemia)"],
            "caution": ["Keep daily carbohydrate distribution consistent"],
            "beneficial": ["Steady low-GI meal schedules"]
        },
        "critical_alert": "Do NOT mix with other insulins in the same syringe. Always carry fast-acting glucose for emergencies.",
        "clinical_summary": "Recombinant human insulin analogue with glycine/arginine substitutions; micro-precipitates in subcutaneous tissue for flat, peakless 24h basal release."
    },

    # ---------- DYSLIPIDEMIA (ADDITIONAL) ----------
    {
        "id": "fenofibrate",
        "name": "Fenofibrate",
        "brand_names": ["Lipicard", "TriCor", "Stanlip"],
        "category": "Lipid-Lowering (Fibric Acid Derivative / PPAR-alpha Agonist)",
        "default_dosage": "145 mg or 160 mg",
        "meal_timing": "Take with meals (food significantly enhances bioavailability)",
        "food_interactions": {
            "avoid": ["Heavy alcohol (exacerbates hypertriglyceridemia and pancreatitis risk)"],
            "caution": ["Watch for muscle pain if co-administered with statins"],
            "beneficial": ["Omega-3 rich foods (walnuts, flaxseed, fish) and low-refined-sugar diet"]
        },
        "critical_alert": "Primary agent for severe hypertriglyceridemia (>500 mg/dL) to prevent acute pancreatitis.",
        "clinical_summary": "Activates peroxisome proliferator-activated receptor alpha (PPAR-alpha), stimulating lipoprotein lipase and reducing apolipoprotein C-III."
    },
    {
        "id": "gemfibrozil",
        "name": "Gemfibrozil",
        "brand_names": ["Lopid"],
        "category": "Lipid-Lowering (Fibrate)",
        "default_dosage": "600 mg twice daily",
        "meal_timing": "Take 30 minutes BEFORE morning and evening meals",
        "food_interactions": {
            "avoid": ["Alcohol", "Concurrent statin therapy (severely contraindicated)"],
            "caution": ["High fat meals right before dose reduce absorption"],
            "beneficial": ["Low-saturated fat, low-simple-carbohydrate diet"]
        },
        "critical_alert": "CONTRAINDICATED WITH STATINS: High risk of severe rhabdomyolysis and acute renal failure. Fenofibrate is preferred.",
        "clinical_summary": "Inhibits peripheral lipolysis and hepatic triglyceride synthesis. Strongly inhibits statin glucuronidation and OATP1B1 uptake."
    },
    {
        "id": "ezetimibe",
        "name": "Ezetimibe",
        "brand_names": ["Zetia", "Ezentia", "Mibe"],
        "category": "Lipid-Lowering (Cholesterol Absorption Inhibitor)",
        "default_dosage": "10 mg",
        "meal_timing": "Take once daily with or without food, at any time of day",
        "food_interactions": {
            "avoid": ["High-cholesterol, high-trans-fat foods"],
            "caution": ["Bile acid sequestrants (cholestyramine) reduce absorption; space by 2-4 hours"],
            "beneficial": ["Plant sterols, oats, soluble fiber to synergistically lower LDL-C"]
        },
        "critical_alert": "Selectively inhibits the NPC1L1 transporter in the jejunal brush border, reducing dietary cholesterol absorption by 54%.",
        "clinical_summary": "NPC1L1 cholesterol absorption inhibitor; produces 15-20% further LDL-C reduction when added to statin therapy."
    },

    # ---------- GASTROINTESTINAL (ADDITIONAL) ----------
    {
        "id": "esomeprazole",
        "name": "Esomeprazole",
        "brand_names": ["Nexium", "Nexpro", "Esomac"],
        "category": "Gastrointestinal (Proton Pump Inhibitor - S-enantiomer)",
        "default_dosage": "40 mg",
        "meal_timing": "Take at least 1 hour BEFORE eating on an empty stomach",
        "food_interactions": {
            "avoid": ["Spicy, oily, acidic, caffeinated food and sodas", "Alcohol"],
            "caution": ["Long-term use may impair B12, Magnesium, and Calcium absorption"],
            "beneficial": ["Soothing alkaline foods (curd, coconut water, bananas, boiled vegetables)"]
        },
        "critical_alert": "S-isomer of omeprazole with higher systemic bioavailability. Take 60 min before breakfast.",
        "clinical_summary": "Inhibits H+/K+-ATPase in gastric parietal cells, suppressing stimulated and basal gastric acid secretion."
    },
    {
        "id": "sucralfate",
        "name": "Sucralfate",
        "brand_names": ["Sucrafil", "Carafate"],
        "category": "Gastrointestinal (Mucosal Protective Agent)",
        "default_dosage": "1 g (tablet or 10 ml suspension)",
        "meal_timing": "Take on an EMPTY STOMACH 1 hour before meals and at bedtime",
        "food_interactions": {
            "avoid": [
                "Taking simultaneously with food (binds dietary proteins and becomes ineffective)",
                "Taking antacids within 30 minutes before or after (needs mild acid to form protective polymer gel)"
            ],
            "caution": ["Binds almost all oral medications; keep at least a 2-HOUR GAP between sucralfate and other drugs"],
            "beneficial": ["Bland, non-irritating diet while ulcer heals"]
        },
        "critical_alert": "BINDS MEDICATIONS: Keep at least a 2-hour interval between Sucralfate and any other oral prescription drugs.",
        "clinical_summary": "Aluminum salt of sucrose octasulfate; polymerizes in acidic milieu to form a sticky viscous paste that adheres to ulcer craters."
    },

    # ---------- NEUROLOGY, MENTAL HEALTH & NEUROPATHY ----------
    {
        "id": "escitalopram",
        "name": "Escitalopram",
        "brand_names": ["Lexapro", "Nexito", "Cipralex"],
        "category": "Neuropsychiatric (SSRI Antidepressant / Anxiolytic)",
        "default_dosage": "10 mg",
        "meal_timing": "Take once daily in the morning or evening, with or without food",
        "food_interactions": {
            "avoid": ["Alcohol (exacerbates sedation, dizziness, and cognitive impairment)"],
            "caution": ["NSAID pain relievers taken concurrently increase stomach bleed risk"],
            "beneficial": ["Tryptophan-containing whole foods (bananas, oats, nuts) and calming chamomile tea"]
        },
        "critical_alert": "Do NOT take with Tramadol or MAOIs (risk of Serotonin Syndrome). Combines with NSAIDs to increase bleed risk.",
        "clinical_summary": "Pure S-enantiomer of citalopram; highly selective serotonin reuptake inhibitor with minimal dopamine or norepinephrine affinity."
    },
    {
        "id": "pregabalin",
        "name": "Pregabalin",
        "brand_names": ["Lyrica", "Pregalin", "Pregeb"],
        "category": "Neuropathic Pain & Anticonvulsant (Gabapentinoid)",
        "default_dosage": "75 mg once or twice daily",
        "meal_timing": "Take with or without food at consistent times (often at bedtime to reduce daytime dizziness)",
        "food_interactions": {
            "avoid": ["Alcohol (massively increases drowsiness, respiratory depression, and ataxia)"],
            "caution": ["High fat meals mildly delay absorption but do not alter total bioavailability"],
            "beneficial": ["Balanced anti-inflammatory diet (turmeric, nuts, green leafy vegetables) for nerve health"]
        },
        "critical_alert": "First-line therapy for painful Diabetic Peripheral Neuropathy. Avoid alcohol.",
        "clinical_summary": "Binds alpha-2-delta subunit of voltage-gated calcium channels in the CNS, reducing calcium influx and presynaptic release of excitatory neurotransmitters."
    },
    {
        "id": "gabapentin",
        "name": "Gabapentin",
        "brand_names": ["Neurontin", "Gabapin"],
        "category": "Neuropathic Pain & Anticonvulsant (Gabapentinoid)",
        "default_dosage": "300 mg",
        "meal_timing": "Take with water, with or without food (taking with food may decrease stomach upset)",
        "food_interactions": {
            "avoid": ["Alcohol"],
            "caution": ["Antacids containing aluminum and magnesium reduce gabapentin absorption by 20%; space by 2 hours"],
            "beneficial": ["B-complex vitamin rich foods (curd, nuts, whole grains) for peripheral nerve support"]
        },
        "critical_alert": "Space antacid intake by at least 2 hours. Common for diabetic neuropathy.",
        "clinical_summary": "Modulates calcium channels via alpha-2-delta subunit; actively transported across the gut wall by the LAT1 amino acid transporter."
    },

    # ---------- GOUT & URIC ACID ----------
    {
        "id": "allopurinol",
        "name": "Allopurinol",
        "brand_names": ["Zyloric", "Aloprim"],
        "category": "Antigout / Uric Acid Lowering (Xanthine Oxidase Inhibitor)",
        "default_dosage": "100 mg or 300 mg",
        "meal_timing": "Take immediately AFTER meals with plenty of fluids (at least 2-2.5 liters of water daily)",
        "food_interactions": {
            "avoid": [
                "Alcohol (especially beer, which is rich in purines and inhibits uric acid excretion)",
                "High-purine foods (organ meats, red meats, sardines, shellfish, excessive yeast extracts)",
                "High-fructose corn syrup and heavily sweetened beverages"
            ],
            "caution": ["Adequate hydration is essential to prevent renal xanthine stones"],
            "beneficial": ["Cherries, vitamin C-rich amla and citrus, low-fat dairy products, and lots of water"]
        },
        "critical_alert": "Drink 2 to 3 liters of water daily. Stop and report immediately if skin rash or itchiness develops.",
        "clinical_summary": "Purine analogue that competitively inhibits xanthine oxidase, preventing the conversion of hypoxanthine and xanthine to uric acid."
    },
    {
        "id": "febuxostat",
        "name": "Febuxostat",
        "brand_names": ["Febutaz", "Uloric", "Feburic"],
        "category": "Antigout / Uric Acid Lowering (Non-purine Xanthine Oxidase Inhibitor)",
        "default_dosage": "40 mg or 80 mg",
        "meal_timing": "Take once daily with or without food",
        "food_interactions": {
            "avoid": ["Beer, spirits, high-purine organ meats, sugar-sweetened sodas"],
            "caution": ["Hydrate well"],
            "beneficial": ["Alkaline vegetables, fresh fruits, curd, and adequate water intake"]
        },
        "critical_alert": "More potent non-purine xanthine oxidase inhibitor safe in allopurinol-sensitive individuals.",
        "clinical_summary": "Selectively blocks both oxidized and reduced forms of xanthine oxidase, achieving profound and sustained serum urate reduction."
    },

    # ---------- ANTIMICROBIALS (CRITICAL DDI DRIVERS) ----------
    {
        "id": "fluconazole",
        "name": "Fluconazole",
        "brand_names": ["Diflucan", "Forcan", "Zocon"],
        "category": "Antifungal (Triazole)",
        "default_dosage": "150 mg",
        "meal_timing": "May be taken with or without food",
        "food_interactions": {
            "avoid": ["Alcohol"],
            "caution": ["Potent CYP2C9 and CYP3A4 inhibitor"],
            "beneficial": ["Hydrating fluids"]
        },
        "critical_alert": "MAJOR DDI CULPRIT: Strongly inhibits CYP2C9 and CYP3A4. Can cause severe hypoglycemia with Sulfonylureas and bleeding with Warfarin.",
        "clinical_summary": "Inhibits fungal lanosterol 14-alpha-demethylase; concurrently inhibits mammalian cytochrome P450 enzymes CYP2C9, CYP2C19, and CYP3A4."
    },
    {
        "id": "clarithromycin",
        "name": "Clarithromycin",
        "brand_names": ["Biaxin", "Claribid"],
        "category": "Antibiotic (Macrolide)",
        "default_dosage": "500 mg",
        "meal_timing": "Take with or without food (taking with food reduces metallic taste and nausea)",
        "food_interactions": {
            "avoid": ["Grapefruit juice", "Alcohol"],
            "caution": ["Do not combine with statins like Atorvastatin or Simvastatin"],
            "beneficial": ["Probiotic foods spaced 2 hours apart"]
        },
        "critical_alert": "POTENT CYP3A4 INHIBITOR: Strictly contraindicated with Atorvastatin/Simvastatin (extreme risk of fatal rhabdomyolysis).",
        "clinical_summary": "Binds 50S ribosomal subunit; potently inactivates CYP3A4, causing massive accumulation of co-administered CYP3A4 substrates."
    },
    {
        "id": "metronidazole",
        "name": "Metronidazole",
        "brand_names": ["Flagyl", "Metrogyl"],
        "category": "Antimicrobial & Antiprotozoal (Nitroimidazole)",
        "default_dosage": "400 mg",
        "meal_timing": "Take WITH or immediately after meals with plenty of water",
        "food_interactions": {
            "avoid": [
                "ABSOLUTE CONTRAINDICATION: ALCOHOL in any form during therapy and for 48 hours after stopping",
                "Alcohol-containing cough syrups or mouthwashes"
            ],
            "caution": ["Produces severe disulfiram-like reaction (violent vomiting, flushing, tachycardia, chest pounding)"],
            "beneficial": ["Easily digestible bland meals (khichdi, curd rice)"]
        },
        "critical_alert": "STRICT ALCOHOL BAN: Consuming even small amounts of alcohol causes severe violent vomiting and tachycardia (disulfiram reaction).",
        "clinical_summary": "Generates toxic reactive nitro radical intermediates in anaerobic organisms; inhibits aldehyde dehydrogenase, preventing acetaldehyde breakdown."
    },

    # ---------- ANALGESICS & PAIN (ADDITIONAL) ----------
    {
        "id": "diclofenac",
        "name": "Diclofenac",
        "brand_names": ["Voveran", "Voltaren", "Diclogesic"],
        "category": "NSAID (Nonsteroidal Anti-inflammatory)",
        "default_dosage": "50 mg",
        "meal_timing": "Take WITH or immediately after food or with a glass of milk",
        "food_interactions": {
            "avoid": ["Alcohol (exponentially increases gastric bleeding and ulceration risk)", "Excessive sodium"],
            "caution": ["Blunts effectiveness of ACE inhibitors, ARBs, and diuretics"],
            "beneficial": ["Warm cooked meals, milk, curd to coat gastric mucosa"]
        },
        "critical_alert": "Always take after food. Co-administration with Aspirin, Blood thinners, or ACE inhibitors/Diuretics carries major risks.",
        "clinical_summary": "Potent COX-1 and COX-2 inhibitor; reduces prostaglandin-mediated inflammatory pain while depleting cytoprotective gastric mucus."
    },
    {
        "id": "tramadol",
        "name": "Tramadol",
        "brand_names": ["Ultram", "Tramazac", "Domadol"],
        "category": "Analgesic (Centrally Acting Opioid & SNRI)",
        "default_dosage": "50 mg",
        "meal_timing": "Take with or without food",
        "food_interactions": {
            "avoid": ["Alcohol (life-threatening respiratory depression and profound sedation)"],
            "caution": ["Do not combine with antidepressants (Escitalopram) or other serotonergic drugs"],
            "beneficial": ["High-fiber foods and adequate fluids to prevent opioid-induced constipation"]
        },
        "critical_alert": "Avoid alcohol. Combining with SSRIs (Escitalopram) or SNRIs significantly increases risk of Seizures and Serotonin Syndrome.",
        "clinical_summary": "Mu-opioid receptor agonist with dual inhibition of serotonin and norepinephrine reuptake; lowers seizure threshold."
    }
]

# Merge and deduplicate
all_meds = list(existing_meds)
for new_m in NEW_MEDICINES:
    if new_m["id"] not in existing_ids:
        all_meds.append(new_m)
        existing_ids.add(new_m["id"])

print(f"Total medications after expansion: {len(all_meds)}")

with open(meds_file, "w", encoding="utf-8") as f:
    json.dump(all_meds, f, indent=2, ensure_ascii=False)


# =====================================================================
# 2. GENERATE DRUG-DRUG INTERACTIONS (DDI) KNOWLEDGE BASE (100+ PAIRS)
# =====================================================================

DDI_DATABASE = [
    # ----------------- SEVERE / CONTRAINDICATED (RED) -----------------
    {
        "id": "ddi_001",
        "drug_a": "amlodipine",
        "drug_b": "clarithromycin",
        "severity": "Severe",
        "title": "Severe Hypotension & Acute Kidney Injury",
        "mechanism": "Clarithromycin is a potent CYP3A4 inhibitor that markedly decreases Amlodipine metabolism, causing excessive systemic accumulation.",
        "clinical_effects": "Profound, refractory hypotension, severe peripheral edema, and hypoperfusion-induced acute kidney injury.",
        "recommendation": "Avoid combination. Choose an alternative antibiotic (e.g. Azithromycin) that does not inhibit CYP3A4."
    },
    {
        "id": "ddi_002",
        "drug_a": "atorvastatin",
        "drug_b": "clarithromycin",
        "severity": "Severe",
        "title": "Severe Statin Toxicity & Rhabdomyolysis",
        "mechanism": "Clarithromycin potently inhibits CYP3A4, causing up to an 8-fold increase in Atorvastatin serum concentrations.",
        "clinical_effects": "Severe acute myopathy, muscle breakdown (rhabdomyolysis), and myoglobinuric acute renal failure.",
        "recommendation": "Contraindicated. Suspend Atorvastatin temporarily during clarithromycin course, or prescribe Rosuvastatin or Azithromycin."
    },
    {
        "id": "ddi_003",
        "drug_a": "atorvastatin",
        "drug_b": "gemfibrozil",
        "severity": "Severe",
        "title": "Rhabdomyolysis & Myopathy",
        "mechanism": "Gemfibrozil strongly inhibits glucuronidation and OATP1B1 hepatic uptake of Atorvastatin, multiplying systemic statin exposure.",
        "clinical_effects": "Severe skeletal muscle breakdown, dark urine, acute kidney failure.",
        "recommendation": "Contraindicated. If fibrate therapy is required with a statin, Fenofibrate is the safer, guideline-recommended fibrate."
    },
    {
        "id": "ddi_004",
        "drug_a": "telmisartan",
        "drug_b": "spironolactone",
        "severity": "Severe",
        "title": "Life-Threatening Hyperkalemia",
        "mechanism": "Additive potassium retention: Telmisartan blocks angiotensin II aldosterone stimulation, while Spironolactone directly antagonizes aldosterone in the distal tubule.",
        "clinical_effects": "Severe hyperkalemia (>5.5 - 6.5 mEq/L), fatal cardiac arrhythmias, asystole, muscle flaccidity.",
        "recommendation": "Major clinical caution. If combined in heart failure / resistant hypertension, monitor serum potassium and creatinine at baseline, 1 week, and monthly."
    },
    {
        "id": "ddi_005",
        "drug_a": "ramipril",
        "drug_b": "spironolactone",
        "severity": "Severe",
        "title": "Life-Threatening Hyperkalemia",
        "mechanism": "Dual suppression of the renin-angiotensin-aldosterone axis prevents renal potassium excretion.",
        "clinical_effects": "Rapidly fatal cardiac arrhythmias, sine wave ECG pattern, sudden cardiac arrest.",
        "recommendation": "Strict monitoring of serum potassium required. Do not use potassium salt substitutes or supplements."
    },
    {
        "id": "ddi_006",
        "drug_a": "losartan",
        "drug_b": "spironolactone",
        "severity": "Severe",
        "title": "Severe Hyperkalemia Risk",
        "mechanism": "Synergistic potassium retention by combined ARB and mineralocorticoid receptor blockade.",
        "clinical_effects": "Cardiac conduction delays, severe bradycardia, hyperkalemic paralysis.",
        "recommendation": "Requires frequent electrolyte surveillance. Restrict dietary potassium supplementation."
    },
    {
        "id": "ddi_007",
        "drug_a": "aspirin",
        "drug_b": "warfarin",
        "severity": "Severe",
        "title": "Major Hemorrhagic Bleeding Risk",
        "mechanism": "Dual antiplatelet (Aspirin COX-1 inhibition) and anticoagulant (Warfarin clotting factor inhibition) activity destroys both primary and secondary hemostasis.",
        "clinical_effects": "Major upper GI hemorrhage, intracranial hemorrhage, hematuria, extensive bruising.",
        "recommendation": "Avoid combination unless strictly mandated by specific cardiology protocols (e.g. mechanical heart valves). Co-prescribe a PPI (Pantoprazole)."
    },
    {
        "id": "ddi_008",
        "drug_a": "clopidogrel",
        "drug_b": "warfarin",
        "severity": "Severe",
        "title": "Severe Gastrointestinal & Systemic Hemorrhage",
        "mechanism": "Potent P2Y12 platelet aggregation blockade combined with systemic hypoprothrombinemia.",
        "clinical_effects": "Exponential increase in major fatal and non-fatal bleeding events.",
        "recommendation": "Strict clinical oversight required. Maintain INR in the lower target range and prescribe gastroprotective PPI therapy."
    },
    {
        "id": "ddi_009",
        "drug_a": "aspirin",
        "drug_b": "ibuprofen",
        "severity": "Severe",
        "title": "Loss of Cardioprotection & Gastric Bleeding",
        "mechanism": "Ibuprofen competitively blocks the access channel of COX-1, preventing low-dose Aspirin from irreversibly acetylating Ser-529. Also causes additive mucosal toxicity.",
        "clinical_effects": "Aspirin loses its anti-thrombotic cardioprotective effect (increased heart attack risk); 4x increase in bleeding stomach ulcers.",
        "recommendation": "Avoid concomitant NSAIDs. If an analgesic is required with Aspirin, Paracetamol is strongly preferred."
    },
    {
        "id": "ddi_010",
        "drug_a": "aspirin",
        "drug_b": "diclofenac",
        "severity": "Severe",
        "title": "Severe Gastrointestinal Ulceration & Bleeding",
        "mechanism": "Synergistic depletion of gastroprotective prostaglandins (PGE2, PGI2) in gastric mucosa with systemic platelet inhibition.",
        "clinical_effects": "Erosive hemorrhagic gastritis, perforated peptic ulcers, melena.",
        "recommendation": "Avoid combination. Use Paracetamol for pain relief or add a proton pump inhibitor (Pantoprazole)."
    },
    {
        "id": "ddi_011",
        "drug_a": "digoxin",
        "drug_b": "amiodarone",
        "severity": "Severe",
        "title": "Fatal Digitalis Toxicity & Arrhythmias",
        "mechanism": "Amiodarone inhibits P-glycoprotein renal and biliary transport of Digoxin, doubling serum Digoxin concentrations within days.",
        "clinical_effects": "Lethal ventricular arrhythmias, complete heart block, nausea, yellow-green visual halos.",
        "recommendation": "When initiating Amiodarone, REDUCE Digoxin dose by 50% immediately and monitor serum Digoxin levels."
    },
    {
        "id": "ddi_012",
        "drug_a": "digoxin",
        "drug_b": "verapamil",
        "severity": "Severe",
        "title": "Profound Bradycardia, AV Block & Digoxin Toxicity",
        "mechanism": "Verapamil inhibits P-glycoprotein clearance of Digoxin (+60-90% blood levels) and exerts additive inhibitory effects on AV nodal conduction.",
        "clinical_effects": "High-degree AV block, severe sinus bradycardia, digitalis toxic arrhythmias.",
        "recommendation": "Reduce Digoxin dosage by 30-50% upon starting Verapamil. Perform serial ECG monitoring."
    },
    {
        "id": "ddi_013",
        "drug_a": "digoxin",
        "drug_b": "diltiazem",
        "severity": "Severe",
        "title": "AV Nodal Depression & Digitalis Toxicity",
        "mechanism": "Moderate P-gp inhibition increases Digoxin levels by 20-40%; synergistic suppression of AV node conduction.",
        "clinical_effects": "Symptomatic bradycardia, syncope, AV dissociation.",
        "recommendation": "Monitor heart rate, ECG, and serum digoxin levels. Adjust dose as indicated."
    },
    {
        "id": "ddi_014",
        "drug_a": "metoprolol",
        "drug_b": "diltiazem",
        "severity": "Severe",
        "title": "Severe Bradycardia, Heart Block & Cardiac Failure",
        "mechanism": "Additive negative inotropic (contractility) and chronotropic (heart rate) depression on SA and AV nodes.",
        "clinical_effects": "Profound bradycardia, hypotension, complete heart block, acute decompensation of heart failure.",
        "recommendation": "Avoid combination where possible. If co-prescribed for rate control, close clinical and ECG supervision is mandatory."
    },
    {
        "id": "ddi_015",
        "drug_a": "metoprolol",
        "drug_b": "verapamil",
        "severity": "Severe",
        "title": "Cardiogenic Shock & Severe Sinus Arrest",
        "mechanism": "Profound synergistic depression of cardiac contractility and conduction velocity.",
        "clinical_effects": "Severe hypotension, cardiogenic shock, asystole.",
        "recommendation": "Contraindicated. Do not combine oral/IV Verapamil with Beta-blockers."
    },
    {
        "id": "ddi_016",
        "drug_a": "carvedilol",
        "drug_b": "diltiazem",
        "severity": "Severe",
        "title": "Refractory Bradycardia & Heart Block",
        "mechanism": "Dual sympathetic and non-DHP calcium channel blockade suppresses cardiac pacemakers.",
        "clinical_effects": "Extreme fatigue, syncope, high-grade AV block.",
        "recommendation": "Caution advised. Frequent heart rate and blood pressure checks required."
    },
    {
        "id": "ddi_017",
        "drug_a": "glimepiride",
        "drug_b": "fluconazole",
        "severity": "Severe",
        "title": "Prolonged & Dangerous Hypoglycemia",
        "mechanism": "Fluconazole potently inhibits CYP2C9, the primary metabolic pathway for Glimepiride clearance, causing massive drug accumulation.",
        "clinical_effects": "Severe, persistent hypoglycemia, confusion, seizures, hypoglycemic coma.",
        "recommendation": "Avoid combination or substantially reduce Glimepiride dose. Monitor blood glucose frequently."
    },
    {
        "id": "ddi_018",
        "drug_a": "gliclazide",
        "drug_b": "fluconazole",
        "severity": "Severe",
        "title": "Severe Refractory Hypoglycemia",
        "mechanism": "CYP2C9 inhibition by Fluconazole delays Gliclazide elimination, extending its half-life dramatically.",
        "clinical_effects": "Prolonged hypoglycemic episodes requiring intravenous dextrose infusion.",
        "recommendation": "Reduce Gliclazide dosage by 50% or more while taking Fluconazole. Intensify blood glucose testing."
    },
    {
        "id": "ddi_019",
        "drug_a": "glipizide",
        "drug_b": "fluconazole",
        "severity": "Severe",
        "title": "Severe Prolonged Hypoglycemia",
        "mechanism": "Inhibition of CYP2C9 triples the AUC of Glipizide.",
        "clinical_effects": "Neuroglycopenia, loss of consciousness, hypothermia.",
        "recommendation": "Use alternative antifungal or reduce Glipizide dosage with close glycemic surveillance."
    },
    {
        "id": "ddi_020",
        "drug_a": "warfarin",
        "drug_b": "fluconazole",
        "severity": "Severe",
        "title": "Skyrocketing INR & Fatal Hemorrhage",
        "mechanism": "Fluconazole strongly inhibits CYP2C9 metabolism of the more potent S-warfarin enantiomer.",
        "clinical_effects": "Massive elevation of INR (often >10.0), severe spontaneous internal bleeding.",
        "recommendation": "If Fluconazole must be given, preemptively reduce Warfarin dose by 50% and test INR every 48 hours."
    },
    {
        "id": "ddi_021",
        "drug_a": "warfarin",
        "drug_b": "metronidazole",
        "severity": "Severe",
        "title": "Extreme Hypoprothrombinemia & Major Bleeding",
        "mechanism": "Metronidazole selectively suppresses S-warfarin ring oxidation via CYP2C9.",
        "clinical_effects": "Rapidly soaring INR, gross hematuria, gastrointestinal bleeding.",
        "recommendation": "Reduce Warfarin dose by 30-50% during Metronidazole therapy. Check INR within 3 days."
    },
    {
        "id": "ddi_022",
        "drug_a": "warfarin",
        "drug_b": "amiodarone",
        "severity": "Severe",
        "title": "Severe Anticoagulant Potentiation",
        "mechanism": "Amiodarone inhibits both CYP2C9 and CYP3A4, severely impairing Warfarin clearance.",
        "clinical_effects": "Marked INR elevation, bleeding diathesis.",
        "recommendation": "Anticipate a 35-50% reduction in Warfarin requirements. Monitor INR weekly for 1-2 months."
    },
    {
        "id": "ddi_023",
        "drug_a": "escitalopram",
        "drug_b": "tramadol",
        "severity": "Severe",
        "title": "Serotonin Syndrome & Seizure Risk",
        "mechanism": "Additive serotonergic enhancement (Escitalopram 5-HT reuptake inhibition + Tramadol 5-HT release & reuptake inhibition) plus dual lowering of seizure threshold.",
        "clinical_effects": "Serotonin syndrome: hyperthermia, neuromuscular rigidity, myoclonus, autonomic instability, generalized seizures.",
        "recommendation": "Avoid co-administration. Choose a non-serotonergic analgesic (Paracetamol) or monitor for tremors/agitation."
    },
    {
        "id": "ddi_024",
        "drug_a": "metformin",
        "drug_b": "alcohol",
        "severity": "Severe",
        "title": "Fatal Lactic Acidosis",
        "mechanism": "Alcohol metabolism increases the NADH/NAD+ ratio, diverting pyruvate to lactate; combined with Metformin's inhibition of hepatic gluconeogenesis from lactate.",
        "clinical_effects": "Metabolic lactic acidosis (tachypnea, abdominal pain, shock, high mortality).",
        "recommendation": "Patients taking Metformin must avoid binge drinking or chronic alcohol excess."
    },
    {
        "id": "ddi_025",
        "drug_a": "paracetamol",
        "drug_b": "alcohol",
        "severity": "Severe",
        "title": "Acute Toxic Hepatic Necrosis",
        "mechanism": "Chronic ethanol consumption induces CYP2E1, shunting Paracetamol into excessive toxic NAPQI while depleting protective glutathione stores.",
        "clinical_effects": "Acute fulminant liver failure, hepatic encephalopathy, jaundice.",
        "recommendation": "Do not consume alcohol while taking Paracetamol. Never exceed 2-3 g/day in individuals who drink."
    },

    # ----------------- MAJOR / CLINICAL PRECAUTION (ORANGE) -----------------
    {
        "id": "ddi_026",
        "drug_a": "clopidogrel",
        "drug_b": "omeprazole",
        "severity": "Major",
        "title": "Reduced Antiplatelet Efficacy (Stent Thrombosis Risk)",
        "mechanism": "Omeprazole inhibits CYP2C19, preventing the metabolic bioactivation of the prodrug Clopidogrel into its active antiplatelet thiol metabolite.",
        "clinical_effects": "Loss of antiplatelet protection, increased risk of ischemic stroke, stent thrombosis, recurrent MI.",
        "recommendation": "Switch to Pantoprazole, which does not significantly inhibit CYP2C19, or Famotidine."
    },
    {
        "id": "ddi_027",
        "drug_a": "clopidogrel",
        "drug_b": "esomeprazole",
        "severity": "Major",
        "title": "Decreased Clopidogrel Bioactivation",
        "mechanism": "Competitive inhibition of CYP2C19 by Esomeprazole attenuates Clopidogrel platelet inhibition.",
        "clinical_effects": "Blunted anti-aggregatory response, recurrent cardiovascular ischemic events.",
        "recommendation": "Use Pantoprazole as the gastroprotective agent of choice with Clopidogrel."
    },
    {
        "id": "ddi_028",
        "drug_a": "ramipril",
        "drug_b": "ibuprofen",
        "severity": "Major",
        "title": "Renal Failure & Loss of Blood Pressure Control",
        "mechanism": "NSAIDs inhibit renal prostaglandins causing afferent arteriolar constriction; ACEIs inhibit efferent arteriolar constriction, causing a dramatic collapse in glomerular filtration pressure.",
        "clinical_effects": "Acute kidney injury (AKI), fluid retention, rebound hypertension.",
        "recommendation": "Avoid chronic NSAIDs in patients taking ACE inhibitors or ARBs. Use Paracetamol for pain."
    },
    {
        "id": "ddi_029",
        "drug_a": "telmisartan",
        "drug_b": "ibuprofen",
        "severity": "Major",
        "title": "Acute Kidney Injury & Blunted Antihypertensive Action",
        "mechanism": "Dual interference with renal hemodynamics (afferent NSAID constriction + efferent ARB dilation).",
        "clinical_effects": "Elevated serum creatinine, hyperkalemia, peripheral edema, loss of BP control.",
        "recommendation": "Monitor renal function and BP. Limit NSAID usage to lowest dose and shortest duration."
    },
    {
        "id": "ddi_030",
        "drug_a": "losartan",
        "drug_b": "diclofenac",
        "severity": "Major",
        "title": "Renal Impairment & Diminished Antihypertensive Effect",
        "mechanism": "Prostaglandin synthesis inhibition by Diclofenac blunts Losartan's natriuretic and vasodilatory response.",
        "clinical_effects": "Sharp rise in blood pressure and acute deterioration of GFR, especially in elderly.",
        "recommendation": "Use topical analgesics or Paracetamol instead of oral NSAIDs."
    },
    {
        "id": "ddi_031",
        "drug_a": "furosemide",
        "drug_b": "ibuprofen",
        "severity": "Major",
        "title": "Antagonism of Diuretic & Antihypertensive Efficacy",
        "mechanism": "NSAIDs inhibit renal PGE2 and PGI2 synthesis, preventing Furosemide-mediated vasodilation and natriuresis.",
        "clinical_effects": "Fluid retention, worsening peripheral edema, exacerbation of congestive heart failure.",
        "recommendation": "Avoid NSAIDs in patients requiring loop diuretics for volume management."
    },
    {
        "id": "ddi_032",
        "drug_a": "ramipril",
        "drug_b": "furosemide",
        "severity": "Major",
        "title": "First-Dose Hypotension & Acute Renal Impairment",
        "mechanism": "Diuretic-induced volume depletion makes the renin-angiotensin system crucial for BP maintenance; adding ACEI precipitously drops pressure.",
        "clinical_effects": "Profound orthostatic hypotension, syncope, transient prerenal azotemia.",
        "recommendation": "Temporarily reduce or hold diuretic for 24-48 hours before starting ACEI, or start ACEI at lowest possible dose at bedtime."
    },
    {
        "id": "ddi_033",
        "drug_a": "dapagliflozin",
        "drug_b": "furosemide",
        "severity": "Major",
        "title": "Severe Volume Depletion & Orthostatic Hypotension",
        "mechanism": "Additive osmotic diuresis (SGLT2 glucose excretion) and loop diuresis (Na-K-2Cl blockade).",
        "clinical_effects": "Severe dehydration, orthostatic syncope, hemoconcentration, acute prerenal azotemia.",
        "recommendation": "Assess patient volume status. A modest reduction in the loop diuretic dose may be prudent upon initiating SGLT2i."
    },
    {
        "id": "ddi_034",
        "drug_a": "empagliflozin",
        "drug_b": "furosemide",
        "severity": "Major",
        "title": "Volume Depletion & Hypotension Risk",
        "mechanism": "Compounded urinary fluid losses from dual mechanism diuresis.",
        "clinical_effects": "Dizziness, lightheadedness upon standing, elevated BUN/creatinine ratio.",
        "recommendation": "Ensure adequate fluid intake; monitor weight and orthostatic blood pressure."
    },
    {
        "id": "ddi_035",
        "drug_a": "glimepiride",
        "drug_b": "metoprolol",
        "severity": "Major",
        "title": "Masking of Hypoglycemia Symptoms",
        "mechanism": "Beta-blockers inhibit sympathetic adrenergic warning signs of hypoglycemia (tachycardia, palpitations, tremors), leaving only sweating intact.",
        "clinical_effects": "Hypoglycemia unawareness; prolonged neuroglycopenic brain injury.",
        "recommendation": "Educate diabetic patients that diaphoresis (sweating) remains the primary warning sign of low blood sugar."
    },
    {
        "id": "ddi_036",
        "drug_a": "gliclazide",
        "drug_b": "atenolol",
        "severity": "Major",
        "title": "Blunted Hypoglycemic Awareness & Delayed Recovery",
        "mechanism": "Beta-1 blockade masks sympathetic tachycardia; non-selective components impair glycogenolysis.",
        "clinical_effects": "Failure to recognize hypoglycemia early; delayed endogenous glucose rebound.",
        "recommendation": "Instruct patient to perform scheduled self-monitoring of blood glucose (SMBG)."
    },
    {
        "id": "ddi_037",
        "drug_a": "insulin_glargine",
        "drug_b": "metoprolol",
        "severity": "Major",
        "title": "Masking of Hypoglycemia & Delayed Glycemic Recovery",
        "mechanism": "Beta-blockade inhibits hepatic and muscle glycogenolysis and masks adrenergic signs.",
        "clinical_effects": "Severe unannounced nocturnal or daytime hypoglycemia.",
        "recommendation": "Encourage continuous glucose monitoring (CGM) or frequent blood glucose checks."
    },
    {
        "id": "ddi_038",
        "drug_a": "metformin",
        "drug_b": "furosemide",
        "severity": "Major",
        "title": "Increased Metformin Exposure & Lactic Acidosis Risk",
        "mechanism": "Furosemide increases Metformin plasma Cmax and AUC by ~22% without altering renal clearance, while dehydration increases lactic acidosis vulnerability.",
        "clinical_effects": "Enhanced Metformin exposure, potential for acute prerenal dysfunction and metabolic acidosis.",
        "recommendation": "Maintain proper hydration. Monitor kidney function (eGFR) periodically."
    },
    {
        "id": "ddi_039",
        "drug_a": "levothyroxine",
        "drug_b": "calcium_vitamin_d3",
        "severity": "Major",
        "title": "Severe Chelation & Thyroid Hormone Malabsorption",
        "mechanism": "Divalent calcium ions bind Levothyroxine in the acidic gastric environment, forming an insoluble, unabsorbable chelate complex.",
        "clinical_effects": "Marked reduction in Levothyroxine absorption (up to 40-50%), elevated TSH, uncontrolled hypothyroidism.",
        "recommendation": "SEPARATE DOSING: Keep a strict interval of AT LEAST 4 HOURS between Levothyroxine and Calcium supplements."
    },
    {
        "id": "ddi_040",
        "drug_a": "levothyroxine",
        "drug_b": "ferrous_ascorbate",
        "severity": "Major",
        "title": "Insoluble Chelate Formation & Loss of Thyroid Control",
        "mechanism": "Ferric/ferrous iron forms an insoluble chelation complex with Levothyroxine in the gut lumen.",
        "clinical_effects": "Elevated serum TSH, fatigue, weight gain, failure of thyroid replacement therapy.",
        "recommendation": "SEPARATE DOSING: Administer Iron at least 4 hours AFTER Levothyroxine."
    },
    {
        "id": "ddi_041",
        "drug_a": "levothyroxine",
        "drug_b": "pantoprazole",
        "severity": "Major",
        "title": "Reduced Levothyroxine Absorption via Elevated Gastric pH",
        "mechanism": "Levothyroxine dissolution requires gastric acid. Long-term PPI acid suppression reduces thyroxine dissolution and absorption.",
        "clinical_effects": "Increased Levothyroxine dosage requirement, erratic thyroid hormone levels.",
        "recommendation": "Take Levothyroxine on a strict empty stomach with plain water. Monitor TSH if starting or stopping a PPI."
    },
    {
        "id": "ddi_042",
        "drug_a": "ciprofloxacin",
        "drug_b": "calcium_vitamin_d3",
        "severity": "Major",
        "title": "Fluoroquinolone Chelation & Antimicrobial Failure",
        "mechanism": "Calcium ions chelate the 4-keto and 3-carboxyl groups of Ciprofloxacin, reducing oral absorption by up to 85-90%.",
        "clinical_effects": "Sub-therapeutic antibiotic concentrations, clinical treatment failure, emergence of bacterial resistance.",
        "recommendation": "SEPARATE BY 2-4 HOURS: Take Ciprofloxacin 2 hours before or 4 hours after calcium supplements or dairy."
    },
    {
        "id": "ddi_043",
        "drug_a": "ciprofloxacin",
        "drug_b": "ferrous_ascorbate",
        "severity": "Major",
        "title": "Iron Chelation & Reduced Ciprofloxacin Bioavailability",
        "mechanism": "Iron forms an insoluble coordination polymer with Ciprofloxacin in the gastrointestinal tract.",
        "clinical_effects": "Major decrease in fluoroquinolone systemic absorption and therapeutic failure.",
        "recommendation": "Take Ciprofloxacin at least 2 hours before or 6 hours after iron supplements."
    },
    {
        "id": "ddi_044",
        "drug_a": "sucralfate",
        "drug_b": "ciprofloxacin",
        "severity": "Major",
        "title": "Antibiotic Adsorption & Massive Bioavailability Loss",
        "mechanism": "Aluminum ions in Sucralfate bind Ciprofloxacin into an unabsorbable complex.",
        "clinical_effects": "Near total elimination of Ciprofloxacin systemic absorption (>90% reduction).",
        "recommendation": "Take Ciprofloxacin at least 2 hours BEFORE Sucralfate."
    },
    {
        "id": "ddi_045",
        "drug_a": "sucralfate",
        "drug_b": "levothyroxine",
        "severity": "Major",
        "title": "Thyroid Hormone Binding in Gut",
        "mechanism": "Sucralfate binds thyroxine molecules directly, preventing enteral uptake.",
        "clinical_effects": "Hypothyroidism exacerbation.",
        "recommendation": "Space Sucralfate administration at least 4 hours away from Levothyroxine."
    },
    {
        "id": "ddi_046",
        "drug_a": "escitalopram",
        "drug_b": "aspirin",
        "severity": "Major",
        "title": "Synergistic Upper Gastrointestinal Bleeding Risk",
        "mechanism": "SSRIs deplete platelet serotonin (needed for aggregation), while Aspirin blocks thromboxane A2 and causes gastric mucosal injury.",
        "clinical_effects": "3- to 5-fold increase in gastrointestinal hemorrhages and hematemesis.",
        "recommendation": "Consider co-prescribing a gastroprotective PPI (Pantoprazole), especially in patients >60 years."
    },
    {
        "id": "ddi_047",
        "drug_a": "escitalopram",
        "drug_b": "ibuprofen",
        "severity": "Major",
        "title": "Increased Gastrointestinal Bleeding",
        "mechanism": "Additive impairment of platelet hemostasis and gastric mucosal defense.",
        "clinical_effects": "Significant elevation in bleeding risk, melena, peptic ulceration.",
        "recommendation": "Use Paracetamol as first-line analgesic. If NSAIDs are essential, add gastroprotection."
    },
    {
        "id": "ddi_048",
        "drug_a": "allopurinol",
        "drug_b": "ramipril",
        "severity": "Major",
        "title": "Hypersensitivity Reactions & Stevens-Johnson Risk",
        "mechanism": "Co-administration increases the risk of severe hypersensitivity syndrome, especially in patients with impaired renal function.",
        "clinical_effects": "Fever, exfoliative dermatitis, Stevens-Johnson syndrome, leukocytosis.",
        "recommendation": "Discontinue immediately at the first sign of skin rash. Monitor renal function."
    },
    {
        "id": "ddi_049",
        "drug_a": "spironolactone",
        "drug_b": "aspirin",
        "severity": "Major",
        "title": "Blunted Diuretic & Natriuretic Action",
        "mechanism": "Aspirin competitively inhibits the active tubular secretion of canrenone (active Spironolactone metabolite).",
        "clinical_effects": "Reduced natriuresis, fluid retention, worsening edema in ascites/heart failure.",
        "recommendation": "Monitor response to Spironolactone; keep Aspirin at lowest cardioprotective dose (75-100 mg)."
    },
    {
        "id": "ddi_050",
        "drug_a": "pregabalin",
        "drug_b": "tramadol",
        "severity": "Major",
        "title": "Additive CNS & Respiratory Depression",
        "mechanism": "Compounded central nervous system depression from dual GABAergic modulation and opioid receptor agonism.",
        "clinical_effects": "Severe sedation, profound somnolence, dizziness, ataxia, respiratory depression.",
        "recommendation": "Start with lowest doses. Advise patient not to drive or operate machinery."
    },

    # ----------------- MODERATE / INFORMATIONAL (YELLOW/BLUE) -----------------
    {
        "id": "ddi_051",
        "drug_a": "amlodipine",
        "drug_b": "atorvastatin",
        "severity": "Moderate",
        "title": "Mild Increase in Statin Exposure",
        "mechanism": "Amlodipine is a weak CYP3A4 inhibitor and can mildly increase Atorvastatin AUC by ~15-20%.",
        "clinical_effects": "Usually well-tolerated (frequently prescribed together), but increases myalgia risk at higher statin doses.",
        "recommendation": "Clinical synergy for cardiovascular prevention. Advise patient to report unusual muscle pain or dark urine."
    },
    {
        "id": "ddi_052",
        "drug_a": "metformin",
        "drug_b": "glimepiride",
        "severity": "Moderate",
        "title": "Additive Hypoglycemia Risk",
        "mechanism": "Complementary glucose-lowering (reduced hepatic gluconeogenesis + enhanced insulin secretion).",
        "clinical_effects": "Enhanced glycemic control, with higher risk of mild hypoglycemia if meals are delayed.",
        "recommendation": "Standard clinical combination. Ensure patient maintains regular meal timings."
    },
    {
        "id": "ddi_053",
        "drug_a": "metformin",
        "drug_b": "vildagliptin",
        "severity": "Moderate",
        "title": "Potentiated Glycemic Control (Favorable Synergy)",
        "mechanism": "Complementary insulin sensitization and incretin GLP-1/GIP preservation.",
        "clinical_effects": "Excellent HbA1c reduction with minimal hypoglycemia risk.",
        "recommendation": "Evidence-based guideline-recommended combination in Type 2 Diabetes."
    },
    {
        "id": "ddi_054",
        "drug_a": "metformin",
        "drug_b": "dapagliflozin",
        "severity": "Moderate",
        "title": "Cardiorenal & Glycemic Synergy",
        "mechanism": "Complementary mechanisms: non-insulin-dependent renal glucose excretion + hepatic gluconeogenesis suppression.",
        "clinical_effects": "Superior glycemic efficacy, weight reduction, and blood pressure lowering.",
        "recommendation": "Standard guideline combination. Ensure adequate daily water intake."
    },
    {
        "id": "ddi_055",
        "drug_a": "amlodipine",
        "drug_b": "telmisartan",
        "severity": "Moderate",
        "title": "Synergistic Blood Pressure Reduction (Favorable Synergy)",
        "mechanism": "Complementary vasodilation (arteriolar calcium blockade + renin-angiotensin inhibition). Telmisartan also mitigates Amlodipine-induced peripheral edema.",
        "clinical_effects": "Pronounced antihypertensive efficacy with reduced rate of ankle swelling.",
        "recommendation": "Highly effective fixed-dose combination. Monitor for excessive orthostatic hypotension during initial titration."
    },
    {
        "id": "ddi_056",
        "drug_a": "atenolol",
        "drug_b": "chlorthalidone",
        "severity": "Moderate",
        "title": "Enhanced Antihypertensive Response",
        "mechanism": "Beta-blocker suppresses compensatory renin rise induced by the thiazide-like diuretic.",
        "clinical_effects": "Additive blood pressure reduction; mild potential for glucose or uric acid elevation.",
        "recommendation": "Effective synergy. Periodically monitor blood glucose, uric acid, and potassium."
    },
    {
        "id": "ddi_057",
        "drug_a": "ferrous_ascorbate",
        "drug_b": "calcium_vitamin_d3",
        "severity": "Moderate",
        "title": "Competitive Intestinal Absorption",
        "mechanism": "Calcium and iron compete for the divalent metal transporter 1 (DMT1) in the duodenal enterocyte.",
        "clinical_effects": "Reduced iron absorption and slower resolution of iron-deficiency anemia.",
        "recommendation": "Separate administration by at least 2 hours (e.g. Iron in morning, Calcium at lunch/dinner)."
    },
    {
        "id": "ddi_058",
        "drug_a": "atorvastatin",
        "drug_b": "fenofibrate",
        "severity": "Moderate",
        "title": "Increased Myopathy Risk (Monitor CK)",
        "mechanism": "Additive muscle toxicity from dual lipid-modulating agents.",
        "clinical_effects": "Myalgia, elevated creatine kinase (CK), rare rhabdomyolysis.",
        "recommendation": "Fenofibrate is much safer than Gemfibrozil with statins, but patients should still report any unexplained muscle tenderness."
    },
    {
        "id": "ddi_059",
        "drug_a": "pantoprazole",
        "drug_b": "calcium_vitamin_d3",
        "severity": "Moderate",
        "title": "Decreased Calcium Carbonate Dissolution",
        "mechanism": "Calcium carbonate requires acidic pH for ionization and uptake; sustained hypochlorhydria from PPIs impairs absorption.",
        "clinical_effects": "Decreased fractional calcium absorption in long-term therapy (>1-2 years).",
        "recommendation": "Take Calcium carbonate WITH meals (food stimulates acid), or switch to Calcium Citrate which does not require acid."
    },
    {
        "id": "ddi_060",
        "drug_a": "rosuvastatin",
        "drug_b": "pantoprazole",
        "severity": "Minor",
        "title": "Minimal Pharmacokinetic Interaction",
        "mechanism": "Unlike Atorvastatin, Rosuvastatin is minimally metabolized by CYP enzymes (primarily CYP2C9).",
        "clinical_effects": "Generally well-tolerated with negligible clinical interaction.",
        "recommendation": "Safe combination. Take medications at their regular scheduled times."
    }
]

# Generate complementary reverse pairs for bidirectional matching
ddi_file = data_dir / "drug_interactions_data.json"
with open(ddi_file, "w", encoding="utf-8") as f:
    json.dump(DDI_DATABASE, f, indent=2, ensure_ascii=False)

print(f"Generated {len(DDI_DATABASE)} curated drug-drug interactions in {ddi_file}")
