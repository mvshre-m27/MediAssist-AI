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
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>🛡️ Clinical Drug Interaction & Safety Checker</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>Automated Pharmacokinetic (CYP450) & Pharmacodynamic Polypharmacy Risk Engine</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "🛡️ Active Regimen Safety Audit",
        "🔍 Multi-Drug Simulator"
    ])

    # =====================================================================
    # TAB 1: MY ACTIVE REGIMEN SAFETY AUDIT
    # =====================================================================
    with tab1:
        regimen_result = ddi.check_patient_regimen_interactions(user_id)
        med_count = regimen_result["active_med_count"]

        if med_count == 0:
            st.info("No active medications found in your profile. Add your prescriptions in the **Medicines** tab.")
        else:
            with st.container(border=True):
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Active Meds", med_count)
                severe_c = regimen_result["severe_count"]
                m_col2.metric("Severe Alerts", severe_c)
                major_c = regimen_result["major_count"]
                m_col3.metric("Major Precautions", major_c)
                m_col4.metric("Moderate / Synergies", regimen_result["moderate_count"])

            if not regimen_result["has_interactions"]:
                st.success("✅ **Regimen Clear:** No adverse drug-drug interactions detected among your currently prescribed medications.")
            else:
                st.markdown(f"#### ⚠️ Identified Regimen Interactions ({regimen_result['total_interactions']})")

                for inter in regimen_result["interactions"]:
                    sev = inter["severity"]
                    if sev == "Severe":
                        border_color = "#ef4444"
                        bg_color = "#fef2f2"
                        badge_cls = "badge-red"
                        icon = "🔴"
                    elif sev == "Major":
                        border_color = "#f59e0b"
                        bg_color = "#fffbeb"
                        badge_cls = "badge-amber"
                        icon = "🟠"
                    else:
                        border_color = "#0284c7"
                        bg_color = "#f0f9ff"
                        badge_cls = "badge-blue"
                        icon = "🟡"

                    with st.container(border=True):
                        hdr1, hdr2 = st.columns([3, 1])
                        with hdr1:
                            st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #0f172a;'>{icon} {inter['drug_1_name']} + {inter['drug_2_name']}</div>", unsafe_allow_html=True)
                            st.caption(f"**Issue:** {inter['title']}")
                        with hdr2:
                            st.markdown(f"<div style='text-align: right;'><span class='badge-pill {badge_cls}'>{sev}</span></div>", unsafe_allow_html=True)

                        st.markdown(f"**Mechanism:** <span style='font-size: 13px; color: #334155;'>{inter['mechanism']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Clinical Consequences:** <span style='font-size: 13px; color: #334155;'>{inter['clinical_effects']}</span>", unsafe_allow_html=True)

                        st.markdown(
                            f"""
                            <div style='background-color: {bg_color}; border-left: 3px solid {border_color}; padding: 8px 12px; border-radius: 4px; margin-top: 8px; font-size: 13px; color: #1e293b;'>
                                <b>Actionable Recommendation:</b> {inter['recommendation']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # -------------------------------------------------------------
            # DRUG-DISEASE CONTRAINDICATIONS (DDeI)
            # -------------------------------------------------------------
            st.markdown("#### 🏥 Drug-Disease & Comorbidity Contraindications")

            ddei_res = ddi.check_patient_drug_disease_interactions(user_id)
            if not ddei_res["has_interactions"]:
                st.success("✅ **No Disease Clashes:** None of your active medications contradict your recorded chronic health conditions.")
            else:
                for clash in ddei_res["interactions"]:
                    c_sev = clash["severity"]
                    c_border = "#ef4444" if c_sev == "Severe" else "#f59e0b"
                    c_bg = "#fef2f2" if c_sev == "Severe" else "#fffbeb"
                    c_badge = "badge-red" if c_sev == "Severe" else "badge-amber"
                    c_icon = "🔴" if c_sev == "Severe" else "🟠"

                    with st.container(border=True):
                        hdr1, hdr2 = st.columns([3, 1])
                        with hdr1:
                            st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #0f172a;'>{c_icon} {clash['matched_drug_name']} ⚡ {clash['disease_name']}</div>", unsafe_allow_html=True)
                            st.caption(f"**Contraindication:** {clash['title']}")
                        with hdr2:
                            st.markdown(f"<div style='text-align: right;'><span class='badge-pill {c_badge}'>{c_sev}</span></div>", unsafe_allow_html=True)

                        st.markdown(f"**Mechanism:** <span style='font-size: 13px; color: #334155;'>{clash['mechanism']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Clinical Impact:** <span style='font-size: 13px; color: #334155;'>{clash['clinical_effects']}</span>", unsafe_allow_html=True)
                        st.markdown(
                            f"""
                            <div style='background-color: {c_bg}; border-left: 3px solid {c_border}; padding: 8px 12px; border-radius: 4px; margin-top: 8px; font-size: 13px; color: #1e293b;'>
                                <b>Physician Action Plan:</b> {clash['action_plan']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    # =====================================================================
    # TAB 2: MULTI-DRUG INTERACTION CHECKER (CUSTOM)
    # =====================================================================
    with tab2:
        all_known = mfi.get_all_known_medicine_names()

        # Preset test buttons
        st.markdown("**Quick Clinical Demo Presets:**")
        p1, p2, p3 = st.columns(3)
        with p1:
            if st.button("🔴 Amlodipine + Clarithromycin", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Amlodipine", "Clarithromycin"]
        with p2:
            if st.button("🔴 Telmisartan + Spironolactone", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Telmisartan", "Spironolactone"]
        with p3:
            if st.button("🟠 Aspirin + Ibuprofen", use_container_width=True):
                st.session_state["ddi_custom_selection"] = ["Aspirin (Low Dose)", "Ibuprofen"]

        default_select = st.session_state.get("ddi_custom_selection", ["Amlodipine", "Atorvastatin"])
        valid_defaults = [k for k in all_known if any(d.lower() in k.lower() for d in default_select)]

        selected_meds = st.multiselect(
            "Select Medications to Test:",
            options=all_known,
            default=valid_defaults,
            placeholder="Search or pick medications..."
        )

        if st.button("🔍 Check Interactions", type="primary", use_container_width=True):
            if len(selected_meds) < 2:
                st.warning("Please select at least **2 medications** to test for pairwise interactions.")
            else:
                analysis = ddi.analyze_custom_medication_list(list(selected_meds))

                with st.container(border=True):
                    r1, r2, r3 = st.columns(3)
                    r1.metric("🔴 Severe Alerts", analysis["severe_count"])
                    r2.metric("🟠 Major Precautions", analysis["major_count"])
                    r3.metric("🟡 Moderate / Notes", analysis["moderate_count"])

                if analysis["total_interactions"] == 0:
                    st.success("✅ **No Interactions Found:** The selected medications have no documented adverse drug-drug interactions in our database.")
                else:
                    for inter in analysis["interactions"]:
                        sev = inter["severity"]
                        if sev == "Severe":
                            icon = "🔴"
                            b_cls = "badge-red"
                            b_line = "#ef4444"
                            b_bg = "#fef2f2"
                        elif sev == "Major":
                            icon = "🟠"
                            b_cls = "badge-amber"
                            b_line = "#f59e0b"
                            b_bg = "#fffbeb"
                        else:
                            icon = "🟡"
                            b_cls = "badge-blue"
                            b_line = "#0284c7"
                            b_bg = "#f0f9ff"

                        with st.container(border=True):
                            hdr1, hdr2 = st.columns([3, 1])
                            with hdr1:
                                st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #0f172a;'>{icon} {inter['drug_1_name']} + {inter['drug_2_name']}</div>", unsafe_allow_html=True)
                                st.caption(f"**Issue:** {inter['title']}")
                            with hdr2:
                                st.markdown(f"<div style='text-align: right;'><span class='badge-pill {b_cls}'>{sev}</span></div>", unsafe_allow_html=True)

                            st.markdown(f"**Mechanism:** <span style='font-size: 13px; color: #334155;'>{inter['mechanism']}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Clinical Impact:** <span style='font-size: 13px; color: #334155;'>{inter['clinical_effects']}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"""
                                <div style='background-color: {b_bg}; border-left: 3px solid {b_line}; padding: 8px 12px; border-radius: 4px; margin-top: 8px; font-size: 13px; color: #1e293b;'>
                                    <b>Clinical Guidance:</b> {inter['recommendation']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
