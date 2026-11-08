
import streamlit as st
from datetime import date, time, timedelta
from database import get_connection
import medicine_food_integration as mfi
import ddi_engine as ddi


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def add_medicine(
    user_id, medicine_name, medicine_type, dosage,
    instructions, start_date, end_date, dose_times,
    total_stock, refill_threshold
):
    """Add a medicine and its schedules for a user."""

    if not medicine_name or not medicine_name.strip():
        return False

    if not dose_times or len(set(dose_times)) != len(dose_times):
        return False

    if total_stock < 0 or refill_threshold < 0:
        return False

    if end_date and end_date < start_date:
        return False

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT INTO medicines (
                user_id, medicine_name, medicine_type, dosage,
                instructions, start_date, end_date,
                total_stock, remaining_stock, refill_threshold
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            medicine_name.strip(),
            medicine_type,
            dosage,
            instructions,
            start_date,
            end_date,
            total_stock,
            total_stock,
            refill_threshold
        ))

        medicine_id = cursor.lastrowid

        for dose_time in dose_times:
            conn.execute("""
                INSERT INTO dose_schedules (medicine_id, dose_time)
                VALUES (?, ?)
            """, (medicine_id, dose_time))

    return True


def get_medicines(user_id):
    """Get medicines belonging to the logged-in user."""

    with get_connection() as conn:
        medicines = conn.execute("""
            SELECT *
            FROM medicines
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()

    return medicines


def get_dose_times(medicine_id, user_id):
    """Get dose timings after checking medicine ownership."""

    with get_connection() as conn:
        schedules = conn.execute("""
            SELECT ds.dose_time
            FROM dose_schedules ds
            JOIN medicines m ON ds.medicine_id = m.id
            WHERE ds.medicine_id = ?
              AND m.user_id = ?
            ORDER BY ds.id
        """, (medicine_id, user_id)).fetchall()

    return [row["dose_time"] for row in schedules]


def update_medicine(
    medicine_id, user_id, medicine_name, medicine_type,
    dosage, instructions, start_date, end_date,
    dose_times, total_stock, refill_threshold
):
    """
    Update medicine details without destroying dose history.

    A schedule with existing dose history cannot be changed
    or removed. New schedules can still be added.
    """

    # ---------------- VALIDATION ----------------

    if not medicine_name or not medicine_name.strip():
        return False

    if not dose_times:
        return False

    if len(set(dose_times)) != len(dose_times):
        return False

    if total_stock < 0 or refill_threshold < 0:
        return False

    if end_date and end_date < start_date:
        return False

    with get_connection() as conn:

        # ---------------- VERIFY OWNERSHIP ----------------

        medicine = conn.execute("""
            SELECT id
            FROM medicines
            WHERE id = ? AND user_id = ?
        """, (medicine_id, user_id)).fetchone()

        if not medicine:
            return False

        # ---------------- GET EXISTING SCHEDULES ----------------

        existing = conn.execute("""
            SELECT id, dose_time
            FROM dose_schedules
            WHERE medicine_id = ?
            ORDER BY id
        """, (medicine_id,)).fetchall()

        existing_ids = [row["id"] for row in existing]
        existing_times = [row["dose_time"] for row in existing]

        # Check which existing schedules have historical records.
        schedules_with_history = set()

        for schedule_id in existing_ids:

            history = conn.execute("""
                SELECT 1
                FROM dose_records
                WHERE schedule_id = ?
                LIMIT 1
            """, (schedule_id,)).fetchone()

            if history:
                schedules_with_history.add(schedule_id)

        # ---------------- CHECK HISTORY BEFORE CHANGES ----------------

        # A schedule with history cannot be removed.
        if len(dose_times) < len(existing_ids):

            surplus_ids = existing_ids[len(dose_times):]

            for schedule_id in surplus_ids:
                if schedule_id in schedules_with_history:
                    return False

        # A schedule with history cannot have its time changed.
        for index, schedule_id in enumerate(existing_ids):

            if index >= len(dose_times):
                break

            if schedule_id in schedules_with_history:

                if existing_times[index] != dose_times[index]:
                    return False

        # ---------------- UPDATE MEDICINE DETAILS ----------------

        cursor = conn.execute("""
            UPDATE medicines
            SET medicine_name = ?,
                medicine_type = ?,
                dosage = ?,
                instructions = ?,
                start_date = ?,
                end_date = ?,
                remaining_stock = MAX(
                    0, remaining_stock + (? - total_stock)
                ),
                total_stock = ?,
                refill_threshold = ?
            WHERE id = ? AND user_id = ?
        """, (
            medicine_name.strip(),
            medicine_type,
            dosage,
            instructions,
            start_date,
            end_date,
            total_stock,
            total_stock,
            refill_threshold,
            medicine_id,
            user_id
        ))

        if cursor.rowcount == 0:
            return False

        # ---------------- UPDATE EXISTING SCHEDULES ----------------

        for index, dose_time in enumerate(dose_times):

            if index < len(existing_ids):

                conn.execute("""
                    UPDATE dose_schedules
                    SET dose_time = ?
                    WHERE id = ?
                """, (dose_time, existing_ids[index]))

            else:

                conn.execute("""
                    INSERT INTO dose_schedules (
                        medicine_id, dose_time
                    )
                    VALUES (?, ?)
                """, (medicine_id, dose_time))

        # ---------------- DELETE UNUSED SCHEDULES ----------------

        surplus_ids = existing_ids[len(dose_times):]

        for schedule_id in surplus_ids:

            conn.execute("""
                DELETE FROM dose_schedules
                WHERE id = ?
            """, (schedule_id,))

    return True


def get_original_stock(medicine_id, user_id):
    """Get original total stock for an owned medicine."""

    with get_connection() as conn:
        result = conn.execute("""
            SELECT total_stock
            FROM medicines
            WHERE id = ?
              AND user_id = ?
        """, (medicine_id, user_id)).fetchone()

    return result["total_stock"] if result else 0


def delete_medicine(medicine_id, user_id):
    """
    Permanently delete a medicine only if it has no dose history.
    This prevents cascading deletion of historical dose records.
    """

    with get_connection() as conn:

        # Check medicine ownership.
        medicine = conn.execute("""
            SELECT id
            FROM medicines
            WHERE id = ? AND user_id = ?
        """, (medicine_id, user_id)).fetchone()

        if not medicine:
            return False

        # Check whether any schedule has dose history.
        history = conn.execute("""
            SELECT 1
            FROM dose_records dr
            JOIN dose_schedules ds
                ON dr.schedule_id = ds.id
            WHERE ds.medicine_id = ?
            LIMIT 1
        """, (medicine_id,)).fetchone()

        if history:
            return False

        cursor = conn.execute("""
            DELETE FROM medicines
            WHERE id = ? AND user_id = ?
        """, (medicine_id, user_id))

    return cursor.rowcount > 0


# ============================================================
# MEDICINE MANAGEMENT UI
# ============================================================

def show_medicines(user_id):

    st.title("💊 Medicine Management")

    st.write(
        "Add and manage your regular and temporary medicines."
    )

    tab1, tab2 = st.tabs([
        "Add Medicine",
        "My Medicines"
    ])

    # ========================================================
    # ADD MEDICINE
    # ========================================================

    with tab1:

        st.subheader("Add a New Medicine")

        # Quick preset selection
        quick_med_options = ["-- Type custom name or pick common medication --"] + mfi.get_all_known_medicine_names()
        selected_preset = st.selectbox(
            "Quick-Select Common Medication (Optional)",
            quick_med_options,
            key="add_quick_preset"
        )

        preset_name = ""
        preset_dosage = ""
        preset_inst = ""

        if selected_preset and not selected_preset.startswith("--"):
            matched_p = mfi.match_medicine_profile(selected_preset)
            if matched_p:
                preset_name = matched_p["name"]
                preset_dosage = matched_p.get("default_dosage", "")
                preset_inst = matched_p.get("meal_timing", "")

        medicine_name = st.text_input(
            "Medicine Name",
            value=preset_name,
            key="add_name"
        )

        medicine_type = st.selectbox(
            "Medicine Type",
            ["regular", "temporary"],
            key="add_type"
        )

        dosage = st.text_input(
            "Dosage (e.g. 1 tablet, 5 ml)",
            value=preset_dosage,
            key="add_dosage"
        )

        instructions = st.text_area(
            "Instructions (optional)",
            value=preset_inst,
            key="add_instructions"
        )

        # Interactive Food-Drug Advisory preview
        if medicine_name and medicine_name.strip():
            matched_profile = mfi.match_medicine_profile(medicine_name)
            if matched_profile:
                with st.container(border=True):
                    st.markdown(f"**🥗 Clinical Food & Dietary Advisory for `{matched_profile['name']}`**")
                    st.caption(f"**Therapeutic Class:** {matched_profile.get('category', 'Standard Medication')}")
                    if matched_profile.get("meal_timing"):
                        st.info(f"🍽️ **Meal Timing:** {matched_profile['meal_timing']}")
                    if matched_profile.get("critical_alert"):
                        st.warning(f"⚠️ **Precaution:** {matched_profile['critical_alert']}")
                    avoid = matched_profile.get("food_interactions", {}).get("avoid", [])
                    if avoid:
                        st.markdown(f"🚫 **Avoid/Caution:** {', '.join(avoid)}")
                    beneficial = matched_profile.get("food_interactions", {}).get("beneficial", [])
                    if beneficial:
                        st.markdown(f"🌟 **Dietary Synergies:** {', '.join(beneficial)}")

            # Proactive Drug-Drug Interaction Check against user's existing prescriptions
            ddi_alerts = ddi.check_new_drug_against_regimen(user_id, medicine_name)
            if ddi_alerts:
                with st.container(border=True):
                    st.markdown("##### ⚠️ Drug-Drug Interaction Warning with Your Current Regimen")
                    for d_alert in ddi_alerts:
                        sev = d_alert["severity"]
                        if sev == "Severe":
                            st.error(
                                f"🔴 **CONTRAINDICATION with {d_alert['existing_medicine']}**: {d_alert['title']}\n\n"
                                f"**Consequence:** {d_alert['clinical_effects']}\n\n"
                                f"**Recommendation:** {d_alert['recommendation']}"
                            )
                        elif sev == "Major":
                            st.warning(
                                f"🟠 **MAJOR PRECAUTION with {d_alert['existing_medicine']}**: {d_alert['title']}\n\n"
                                f"**Consequence:** {d_alert['clinical_effects']}\n\n"
                                f"**Recommendation:** {d_alert['recommendation']}"
                            )
                        else:
                            st.info(f"🟡 **Notice with {d_alert['existing_medicine']}**: {d_alert['title']}")

            # Proactive Drug-Disease Contraindication Check
            ddei_alerts = ddi.check_new_drug_against_diseases(user_id, medicine_name)
            if ddei_alerts:
                with st.container(border=True):
                    st.markdown("##### ⚠️ Drug-Disease Contraindication Warning")
                    for ddei in ddei_alerts:
                        d_sev = ddei["severity"]
                        if d_sev == "Severe":
                            st.error(
                                f"🔴 **CONTRAINDICATION with your condition ({ddei['disease_name']})**: {ddei['title']}\n\n"
                                f"**Impact:** {ddei['clinical_effects']}\n\n"
                                f"**Guidance:** {ddei['action_plan']}"
                            )
                        elif d_sev == "Major":
                            st.warning(
                                f"🟠 **MAJOR CAUTION with your condition ({ddei['disease_name']})**: {ddei['title']}\n\n"
                                f"**Impact:** {ddei['clinical_effects']}\n\n"
                                f"**Guidance:** {ddei['action_plan']}"
                            )
                        else:
                            st.info(f"🟡 **Notice for ({ddei['disease_name']})**: {ddei['title']}")

        st.write("### Schedule")

        frequency = st.selectbox(
            "Doses per day",
            [1, 2, 3, 4],
            key="add_frequency"
        )

        default_times = [
            time(8, 0),
            time(13, 0),
            time(18, 0),
            time(21, 0)
        ]

        dose_times = []

        for i in range(frequency):

            selected_time = st.time_input(
                f"Dose {i + 1} time",
                value=default_times[i],
                key=f"add_dose_time_{i}"
            )

            dose_times.append(
                selected_time.strftime("%H:%M")
            )

        st.write("### Duration")

        start_date = st.date_input(
            "Start Date",
            value=date.today(),
            key="add_start"
        )

        end_date = None

        if medicine_type == "temporary":

            end_date = st.date_input(
                "End Date",
                value=date.today() + timedelta(days=5),
                min_value=start_date,
                key="add_end"
            )

        st.write("### Stock Details")

        total_stock = st.number_input(
            "Total Stock",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="add_stock"
        )

        refill_threshold = st.number_input(
            "Refill Reminder Threshold",
            min_value=0.0,
            value=5.0,
            step=1.0,
            key="add_threshold"
        )

        if st.button(
            "Add Medicine",
            use_container_width=True
        ):

            if not medicine_name.strip():

                st.error("Please enter the medicine name.")

            elif end_date and end_date < start_date:

                st.error("End date cannot be before start date.")

            else:

                success = add_medicine(
                    user_id,
                    medicine_name,
                    medicine_type,
                    dosage.strip(),
                    instructions.strip(),
                    start_date.isoformat(),
                    end_date.isoformat() if end_date else None,
                    dose_times,
                    total_stock,
                    refill_threshold
                )

                if success:

                    st.success("Medicine added successfully!")
                    st.rerun()

                else:

                    st.error(
                        "Unable to add medicine. Please check the details."
                    )

    # ========================================================
    # VIEW AND MANAGE MEDICINES
    # ========================================================

    with tab2:

        st.subheader("Your Medicines")

        medicines = get_medicines(user_id)

        # Regimen Drug-Drug Interaction Scan summary banner
        regimen_ddi = ddi.check_patient_regimen_interactions(user_id)
        if regimen_ddi["has_interactions"]:
            s_c = regimen_ddi["severe_count"]
            m_c = regimen_ddi["major_count"]
            if s_c > 0:
                st.error(
                    f"⚠️ **Clinical Medication Alert:** Identified **{s_c} Severe** interaction(s) in your active prescriptions. "
                    f"Visit the **Drug Interaction Checker** in the sidebar to review the full interaction mechanism and doctor guidance."
                )
            elif m_c > 0:
                st.warning(
                    f"⚠️ **Polypharmacy Precaution:** Identified **{m_c} Major** interaction(s) in your active prescriptions. "
                    f"Review dose timing and precautions under the **Drug Interaction Checker** tab."
                )

        if not medicines:

            st.info("No medicines added yet.")

        else:

            for medicine in medicines:

                medicine_id = medicine["id"]

                medicine_label = (
                    "Regular"
                    if medicine["medicine_type"] == "regular"
                    else "Temporary"
                )

                with st.expander(
                    f"💊 {medicine['medicine_name']} ({medicine_label})"
                ):

                    st.write(
                        f"**Dosage:** "
                        f"{medicine['dosage'] or 'Not specified'}"
                    )

                    st.write(
                        f"**Instructions:** "
                        f"{medicine['instructions'] or 'None'}"
                    )

                    st.write(
                        f"**Start Date:** {medicine['start_date']}"
                    )

                    st.write(
                        f"**End Date:** "
                        f"{medicine['end_date'] or 'Ongoing'}"
                    )

                    dose_times = get_dose_times(
                        medicine_id,
                        user_id
                    )

                    st.write(
                        "**Dose Timings:** "
                        + (
                            ", ".join(dose_times)
                            if dose_times else "None"
                        )
                    )

                    st.write(
                        f"**Remaining Stock:** "
                        f"{medicine['remaining_stock']}"
                    )

                    if (
                        medicine["remaining_stock"]
                        <= medicine["refill_threshold"]
                    ):

                        st.warning(
                            "Stock is low. Consider checking your refill."
                        )

                    # Food & Nutrition Guidance Expander
                    med_profile = mfi.match_medicine_profile(medicine["medicine_name"])
                    if med_profile:
                        with st.expander("🥗 Food & Nutrition Guidance for this Medicine", expanded=False):
                            st.caption(f"**Therapeutic Class:** {med_profile.get('category', 'Standard Medication')}")
                            if med_profile.get("meal_timing"):
                                st.markdown(f"🍽️ **Meal Timing:** {med_profile['meal_timing']}")
                            if med_profile.get("critical_alert"):
                                st.warning(f"⚠️ **Precaution:** {med_profile['critical_alert']}")
                            avoid = med_profile.get("food_interactions", {}).get("avoid", [])
                            if avoid:
                                st.markdown(f"🚫 **Foods/Substances to Avoid:** {', '.join(avoid)}")
                            beneficial = med_profile.get("food_interactions", {}).get("beneficial", [])
                            if beneficial:
                                st.markdown(f"🌟 **Dietary Synergies:** {', '.join(beneficial)}")
                            if med_profile.get("clinical_summary"):
                                st.caption(f"ℹ️ *Pharmacology Note:* {med_profile['clinical_summary']}")
                    else:
                        with st.expander("🥗 Food & Nutrition Guidance", expanded=False):
                            st.caption("Take as directed with water. Keep a consistent meal routine and consult your doctor or dietitian regarding specific food precautions.")

                    edit_col, delete_col = st.columns(2)

                    # ====================================================
                    # EDIT MEDICINE
                    # ====================================================

                    with edit_col:

                        if st.button(
                            "Edit",
                            key=f"edit_{medicine_id}"
                        ):

                            st.session_state[
                                f"editing_{medicine_id}"
                            ] = True

                    if st.session_state.get(
                        f"editing_{medicine_id}", False
                    ):

                        with st.form(
                            f"edit_form_{medicine_id}"
                        ):

                            new_name = st.text_input(
                                "Medicine Name",
                                value=medicine["medicine_name"]
                            )

                            new_type = st.selectbox(
                                "Medicine Type",
                                ["regular", "temporary"],
                                index=(
                                    0
                                    if medicine["medicine_type"] == "regular"
                                    else 1
                                )
                            )

                            new_dosage = st.text_input(
                                "Dosage",
                                value=medicine["dosage"] or ""
                            )

                            new_instructions = st.text_area(
                                "Instructions",
                                value=medicine["instructions"] or ""
                            )

                            old_times = get_dose_times(
                                medicine_id,
                                user_id
                            )

                            new_frequency = st.selectbox(
                                "Doses per day",
                                [1, 2, 3, 4],
                                index=min(
                                    max(len(old_times), 1), 4
                                ) - 1
                            )

                            new_times = []

                            for i in range(new_frequency):

                                old_time = (
                                    time.fromisoformat(old_times[i])
                                    if i < len(old_times)
                                    else default_times[i]
                                )

                                chosen_time = st.time_input(
                                    f"Dose {i + 1} time",
                                    value=old_time,
                                    key=f"edit_time_{medicine_id}_{i}"
                                )

                                new_times.append(
                                    chosen_time.strftime("%H:%M")
                                )

                            new_start = st.date_input(
                                "Start Date",
                                value=date.fromisoformat(
                                    medicine["start_date"]
                                ),
                                key=f"edit_start_{medicine_id}"
                            )

                            new_end = None

                            if new_type == "temporary":

                                default_end = (
                                    date.fromisoformat(
                                        medicine["end_date"]
                                    )
                                    if medicine["end_date"]
                                    else new_start + timedelta(days=5)
                                )

                                new_end = st.date_input(
                                    "End Date",
                                    value=max(default_end, new_start),
                                    min_value=new_start,
                                    key=f"edit_end_{medicine_id}"
                                )

                            new_stock = st.number_input(
                                "Total Stock",
                                min_value=0.0,
                                value=float(medicine["total_stock"]),
                                step=1.0,
                                key=f"edit_stock_{medicine_id}"
                            )

                            new_threshold = st.number_input(
                                "Refill Threshold",
                                min_value=0.0,
                                value=float(
                                    medicine["refill_threshold"]
                                ),
                                step=1.0,
                                key=f"edit_threshold_{medicine_id}"
                            )

                            save = st.form_submit_button(
                                "Save Changes"
                            )

                            if save:

                                if not new_name.strip():

                                    st.error(
                                        "Medicine name is required."
                                    )

                                elif new_end and new_end < new_start:

                                    st.error(
                                        "End date cannot be before start date."
                                    )

                                else:

                                    success = update_medicine(
                                        medicine_id,
                                        user_id,
                                        new_name.strip(),
                                        new_type,
                                        new_dosage.strip(),
                                        new_instructions.strip(),
                                        new_start.isoformat(),
                                        new_end.isoformat()
                                        if new_end else None,
                                        new_times,
                                        new_stock,
                                        new_threshold
                                    )

                                    if success:

                                        st.session_state[
                                            f"editing_{medicine_id}"
                                        ] = False

                                        st.success(
                                            "Medicine updated successfully!"
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            "Medicine could not be updated. "
                                            "A schedule with dose history "
                                            "may have been changed or removed. "
                                            "Preserving your dose history "
                                            "requires keeping that schedule "
                                            "unchanged."
                                        )

                    # ====================================================
                    # DELETE MEDICINE
                    # ====================================================

                    with delete_col:

                        if st.button(
                            "Delete",
                            key=f"delete_{medicine_id}"
                        ):

                            st.session_state[
                                f"deleting_{medicine_id}"
                            ] = True

                    if st.session_state.get(
                        f"deleting_{medicine_id}", False
                    ):

                        st.warning(
                            "Are you sure you want to delete this medicine?"
                        )

                        confirm_col, cancel_col = st.columns(2)

                        with confirm_col:

                            if st.button(
                                "Confirm Delete",
                                key=f"confirm_delete_{medicine_id}"
                            ):

                                deleted = delete_medicine(
                                    medicine_id,
                                    user_id
                                )

                                if deleted:

                                    st.success("Medicine deleted.")

                                else:

                                    st.error(
                                        "This medicine has dose history "
                                        "and cannot be permanently deleted. "
                                        "Your history has been protected."
                                    )

                                st.rerun()

                        with cancel_col:

                            if st.button(
                                "Cancel",
                                key=f"cancel_delete_{medicine_id}"
                            ):

                                st.session_state[
                                    f"deleting_{medicine_id}"
                                ] = False

                                st.rerun()
