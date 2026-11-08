"""
Drug-Drug Interaction (DDI) Checker User Interface
--------------------------------------------------
Clinical Polypharmacy Risk Analyzer allowing patients and healthcare
professionals to audit active prescriptions and run custom interaction checks.
"""

import streamlit as st
import ddi_engine as ddi
import medicine_food_integration as mfi

def show_ddi_checker_page(user_id):
    st.title("💊 Automated Drug-Drug Interaction (DDI) Checker")
    st.caption("Evidence-Based Polypharmacy Safety Engine | Grounded in Pharmacokinetic & Pharmacodynamic Clinical Pharmacology")

    # Safety Notice
    st.info(
        "💡 **Clinical Pharmacology Notice:** This automated engine analyzes adverse drug-drug interactions (CYP450 inhibition/induction, "
        "renal clearance competition, additive bleeding, arrhythmias, and electrolyte shifts). "
        "It supports informed decision-making but does NOT replace clinical judgment by your treating physician."
    )

    tab1, tab2 = st.tabs([
        "🛡️ My Active Regimen Safety Audit",
        "🔍 Multi-Drug Interaction Checker"
    ])

    # =====================================================================
    # TAB 1: MY ACTIVE REGIMEN SAFETY AUDIT
    # =====================================================================
    with tab1:
        st.subheader("Active Prescription Safety Audit")
        st.caption("Automated all-pairs scan of your currently saved medications in MediAssist.")

        regimen_result = ddi.check_patient_regimen_interactions(user_id)
        med_count = regimen_result["active_med_count"]

        if med_count == 0:
            st.info("No active medications found in your profile. Add your prescriptions in the **Medicines** tab to run an automated safety audit.")
        else:
            # Summary Metrics Bar
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.metric("Prescribed Meds", med_count)
            with m_col2:
                severe_c = regimen_result["severe_count"]
                st.metric("Severe (Contraindicated)", severe_c, delta=None if severe_c == 0 else f"{severe_c} Alert", delta_color="inverse")
            with m_col3:
                major_c = regimen_result["major_count"]
                st.metric("Major Precautions", major_c, delta=None if major_c == 0 else f"{major_c} Caution", delta_color="inverse")
            with m_col4:
                mod_c = regimen_result["moderate_count"]
                st.metric("Moderate / Synergies", mod_c)

            st.divider()

            if not regimen_result["has_interactions"]:
                st.success(
                    "✅ **Regimen Clear:** No adverse drug-drug interactions detected among your currently prescribed medications. "
                    "Always notify your physician before starting any new over-the-counter drugs or supplements."
                )
            else:
                st.markdown(f"#### ⚠️ Identified Interactions ({regimen_result['total_interactions']} Found)")

                for idx, inter in enumerate(regimen_result["interactions"]):
                    sev = inter["severity"]

                    if sev == "Severe":
                        border_color = "#d32f2f"
                        badge_bg = "#ffebee"
                        badge_color = "#c62828"
                        icon = "🔴"
                    elif sev == "Major":
                        border_color = "#ed6c02"
                        badge_bg = "#fff3e0"
                        badge_color = "#e65100"
                        icon = "🟠"
                    elif sev == "Moderate":
                        border_color = "#0288d1"
                        badge_bg = "#e1f5fe"
                        badge_color = "#01579b"
                        icon = "🟡"
                    else:
                        border_color = "#757575"
                        badge_bg = "#f5f5f5"
                        badge_color = "#424242"
                        icon = "🔵"

                    with st.container(border=True):
                        col_hdr1, col_hdr2 = st.columns([3, 1])
                        with col_hdr1:
                            st.markdown(
                                f"### {icon} {inter['drug_1_name']} + {inter['drug_2_name']}"
                            )
                            st.markdown(f"**Clinical Issue:** `{inter['title']}`")
                        with col_hdr2:
                            st.markdown(
                                f"<div style='text-align: right;'><span style='background-color: {badge_bg}; color: {badge_color}; "
                                f"padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px; text-transform: uppercase;'>"
                                f"{sev}</span></div>",
                                unsafe_allow_html=True
                            )

                        st.markdown(f"**🔬 Mechanism:** {inter['mechanism']}")
                        st.markdown(f"**⚠️ Clinical Consequences:** {inter['clinical_effects']}")

                        st.markdown(
                            f"""
                            <div style='background-color: #f8f9fa; border-left: 4px solid {border_color}; padding: 10px 14px; border-radius: 4px; margin-top: 10px;'>
                                <strong style='color: #212529;'>📋 Actionable Clinical Recommendation:</strong><br>
                                <span style='color: #333;'>{inter['recommendation']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.divider()

            # -------------------------------------------------------------
            # DRUG-DISEASE CONTRAINDICATIONS (DDeI)
            # -------------------------------------------------------------
            st.subheader("🏥 Drug-Disease & Comorbidity Contraindications")
            st.caption("Checks whether any prescribed medications contradict your diagnosed chronic medical conditions.")

            ddei_res = ddi.check_patient_drug_disease_interactions(user_id)
            if not ddei_res["has_interactions"]:
                st.success(
                    "✅ **No Drug-Disease Contraindications:** None of your active medications contradict your recorded chronic health conditions."
                )
            else:
                st.markdown(f"#### ⚠️ Identified Disease Clashes ({ddei_res['total_interactions']} Found)")
                for clash in ddei_res["interactions"]:
                    c_sev = clash["severity"]
                    c_icon = "🔴" if c_sev == "Severe" else "🟠"
                    c_border = "#d32f2f" if c_sev == "Severe" else "#ed6c02"
                    c_bg = "#ffebee" if c_sev == "Severe" else "#fff3e0"
                    c_color = "#c62828" if c_sev == "Severe" else "#e65100"

                    with st.container(border=True):
                        hdr_col1, hdr_col2 = st.columns([3, 1])
                        with hdr_col1:
                            st.markdown(f"### {c_icon} {clash['matched_drug_name']} ⚡ {clash['disease_name']}")
                            st.markdown(f"**Contraindication:** `{clash['title']}`")
                        with hdr_col2:
                            st.markdown(
                                f"<div style='text-align: right;'><span style='background-color: {c_bg}; color: {c_color}; "
                                f"padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px; text-transform: uppercase;'>"
                                f"{c_sev}</span></div>",
                                unsafe_allow_html=True
                            )

                        st.markdown(f"**🔬 Pharmacological Mechanism:** {clash['mechanism']}")
                        st.markdown(f"**⚠️ Clinical Impact on Disease:** {clash['clinical_effects']}")
                        st.markdown(
                            f"""
                            <div style='background-color: #f8f9fa; border-left: 4px solid {c_border}; padding: 10px 14px; border-radius: 4px; margin-top: 10px;'>
                                <strong style='color: #212529;'>📋 Clinical Physician Action Plan:</strong><br>
                                <span style='color: #333;'>{clash['action_plan']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    # =====================================================================
    # TAB 2: MULTI-DRUG INTERACTION CHECKER (CUSTOM)
    # =====================================================================
    with tab2:
        st.subheader("Interactive Multi-Drug Interaction Checker")
        st.caption("Select any two or more medications to analyze potential polypharmacy interactions.")

        all_known = mfi.get_all_known_medicine_names()

        # Preset test buttons for quick demo
        st.markdown("**Quick Clinical Presets for Testing:**")
        preset_cols = st.columns(3)

        with preset_cols[0]:
            if st.button("🔴 Amlodipine + Clarithromycin", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Amlodipine", "Clarithromycin"]
        with preset_cols[1]:
            if st.button("🔴 Telmisartan + Spironolactone", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Telmisartan", "Spironolactone"]
        with preset_cols[2]:
            if st.button("🟠 Aspirin + Ibuprofen", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Aspirin (Low Dose)", "Ibuprofen"]

        preset_cols2 = st.columns(3)
        with preset_cols2[0]:
            if st.button("🟠 Clopidogrel + Omeprazole", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Clopidogrel", "Omeprazole"]
        with preset_cols2[1]:
            if st.button("🔴 Digoxin + Amiodarone", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Digoxin", "Amiodarone"]
        with preset_cols2[2]:
            if st.button("🟠 Levothyroxine + Calcium", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Levothyroxine", "Calcium Carbonate + Vitamin D3"]

        default_select = st.session_state.get("ddi_custom_selection", ["Amlodipine", "Atorvastatin"])

        # Filter default selection to valid items in all_known
        valid_defaults = []
        for d in default_select:
            matched = False
            for k in all_known:
                if d.lower() in k.lower():
                    valid_defaults.append(k)
                    matched = True
                    break
            if not matched and d in all_known:
                valid_defaults.append(d)

        selected_meds = st.multiselect(
            "Select Medications to Test:",
            options=all_known,
            default=valid_defaults,
            placeholder="Search or pick medications (e.g., Metformin, Amlodipine, Telmisartan, Aspirin, Ibuprofen, Clarithromycin...)"
        )

        custom_extra = st.text_input("Or type additional medicine names (comma-separated):", placeholder="e.g. Warfarin, Escitalopram")

        if st.button("🔍 Run Comprehensive Safety Check", type="primary", use_container_width=True):
            combined_list = list(selected_meds)
            if custom_extra and custom_extra.strip():
                for item in custom_extra.split(","):
                    if item.strip():
                        combined_list.append(item.strip())

            if len(combined_list) < 2:
                st.warning("Please select or enter at least **2 medications** to check for interactions.")
            else:
                analysis = ddi.analyze_custom_medication_list(combined_list)

                st.write(f"Analyzed **{analysis['total_drugs_checked']} medications** across all pairwise combinations:")

                s_c = analysis["severe_count"]
                m_c = analysis["major_count"]
                mod_c = analysis["moderate_count"]

                r_col1, r_col2, r_col3 = st.columns(3)
                with r_col1:
                    st.metric("🔴 Severe Interactions", s_c)
                with r_col2:
                    st.metric("🟠 Major Precautions", m_c)
                with r_col3:
                    st.metric("🟡 Moderate / Notes", mod_c)

                st.divider()

                if analysis["total_interactions"] == 0:
                    st.success("✅ **No Interactions Found:** The selected medications have no documented major adverse drug-drug interactions in our clinical database.")
                else:
                    for inter in analysis["interactions"]:
                        sev = inter["severity"]
                        if sev == "Severe":
                            icon = "🔴"
                            b_bg = "#ffebee"
                            b_c = "#c62828"
                            b_line = "#d32f2f"
                        elif sev == "Major":
                            icon = "🟠"
                            b_bg = "#fff3e0"
                            b_c = "#e65100"
                            b_line = "#ed6c02"
                        else:
                            icon = "🟡"
                            b_bg = "#e1f5fe"
                            b_c = "#01579b"
                            b_line = "#0288d1"

                        with st.container(border=True):
                            hdr1, hdr2 = st.columns([3, 1])
                            with hdr1:
                                st.markdown(f"#### {icon} {inter['drug_1_name']} + {inter['drug_2_name']}")
                                st.markdown(f"**Issue:** `{inter['title']}`")
                            with hdr2:
                                st.markdown(
                                    f"<div style='text-align: right;'><span style='background-color: {b_bg}; color: {b_c}; "
                                    f"padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; text-transform: uppercase;'>"
                                    f"{sev}</span></div>",
                                    unsafe_allow_html=True
                                )

                            st.markdown(f"**Mechanism:** {inter['mechanism']}")
                            st.markdown(f"**Clinical Impact:** {inter['clinical_effects']}")
                            st.markdown(
                                f"""
                                <div style='background-color: #f8f9fa; border-left: 4px solid {b_line}; padding: 8px 12px; border-radius: 4px; margin-top: 8px;'>
                                    <strong style='color: #212529;'>Clinical Guidance:</strong> {inter['recommendation']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
