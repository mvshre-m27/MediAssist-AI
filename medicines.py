
import streamlit as st
from datetime import date, time, timedelta
from database import get_connection


# -------------------- DATABASE FUNCTIONS --------------------

def add_medicine(
    user_id, medicine_name, medicine_type, dosage,
    instructions, start_date, end_date, dose_times,
    total_stock, refill_threshold
):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO medicines (
                user_id, medicine_name, medicine_type, dosage,
                instructions, start_date, end_date,
                total_stock, remaining_stock, refill_threshold
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, medicine_name, medicine_type, dosage,
            instructions, start_date, end_date,
            total_stock, total_stock, refill_threshold
        ))

        medicine_id = cursor.lastrowid

        for dose_time in dose_times:
            conn.execute("""
                INSERT INTO dose_schedules (medicine_id, dose_time)
                VALUES (?, ?)
            """, (medicine_id, dose_time))

    return True


def get_medicines(user_id):
    with get_connection() as conn:
        medicines = conn.execute("""
            SELECT * FROM medicines
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()

        return medicines


def get_dose_times(medicine_id):
    with get_connection() as conn:
        schedules = conn.execute("""
            SELECT dose_time FROM dose_schedules
            WHERE medicine_id = ?
            ORDER BY dose_time
        """, (medicine_id,)).fetchall()

        return [row["dose_time"] for row in schedules]

def update_medicine(
    medicine_id, user_id, medicine_name, medicine_type,
    dosage, instructions, start_date, end_date,
    dose_times, total_stock, refill_threshold
):
    with get_connection() as conn:

        conn.execute("""
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
            medicine_name, medicine_type, dosage,
            instructions, start_date, end_date,
            total_stock, total_stock, refill_threshold,
            medicine_id, user_id
        ))

        conn.execute("""
            DELETE FROM dose_schedules
            WHERE medicine_id = ?
        """, (medicine_id,))

        for dose_time in dose_times:
            conn.execute("""
                INSERT INTO dose_schedules (medicine_id, dose_time)
                VALUES (?, ?)
            """, (medicine_id, dose_time))


def get_original_stock(medicine_id, user_id):
    with get_connection() as conn:
        result = conn.execute("""
            SELECT total_stock FROM medicines
            WHERE id = ? AND user_id = ?
        """, (medicine_id, user_id)).fetchone()

        return result["total_stock"] if result else 0


def delete_medicine(medicine_id, user_id):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM medicines
            WHERE id = ? AND user_id = ?
        """, (medicine_id, user_id))


# -------------------- MEDICINE MANAGEMENT UI --------------------

def show_medicines(user_id):

    st.title("💊 Medicine Management")
    st.write("Add and manage your regular and temporary medicines.")

    tab1, tab2 = st.tabs(["Add Medicine", "My Medicines"])

    # -------------------- ADD MEDICINE --------------------


    with tab1:
        st.subheader("Add a New Medicine")

        medicine_name = st.text_input("Medicine Name", key="add_name")

        medicine_type = st.selectbox(
            "Medicine Type",
            ["regular", "temporary"],
            key="add_type"
        )

        dosage = st.text_input("Dosage (e.g. 1 tablet, 5 ml)", key="add_dosage")

        instructions = st.text_area("Instructions (optional)", key="add_instructions")

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
            dose_times.append(selected_time.strftime("%H:%M"))

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

        if st.button("Add Medicine", use_container_width=True):

            if not medicine_name.strip():
                st.error("Please enter the medicine name.")

            elif end_date and end_date < start_date:
                st.error("End date cannot be before start date.")

            else:
                add_medicine(
                    user_id,
                    medicine_name.strip(),
                    medicine_type,
                    dosage.strip(),
                    instructions.strip(),
                    start_date.isoformat(),
                    end_date.isoformat() if end_date else None,
                    dose_times,
                    total_stock,
                    refill_threshold
                )

                st.success("Medicine added successfully!")
                st.rerun()


    # -------------------- VIEW MEDICINES --------------------

    with tab2:

        st.subheader("Your Medicines")

        medicines = get_medicines(user_id)

        if not medicines:
            st.info("No medicines added yet.")

        else:
            for medicine in medicines:

                medicine_id = medicine["id"]

                with st.expander(
                    f"💊 {medicine['medicine_name']} "
                    f"({'Regular' if medicine['medicine_type'] == 'regular' else 'Temporary'})"
                ):

                    st.write(f"**Dosage:** {medicine['dosage'] or 'Not specified'}")
                    st.write(f"**Instructions:** {medicine['instructions'] or 'None'}")
                    st.write(f"**Start Date:** {medicine['start_date']}")
                    st.write(f"**End Date:** {medicine['end_date'] or 'Ongoing'}")

                    dose_times = get_dose_times(medicine_id)

                    st.write(
                        "**Dose Timings:** " +
                        (", ".join(dose_times) if dose_times else "None")
                    )

                    st.write(
                        f"**Remaining Stock:** {medicine['remaining_stock']}"
                    )

                    if medicine["remaining_stock"] <= medicine["refill_threshold"]:
                        st.warning("Stock is low. Consider checking your refill.")

                    edit_col, delete_col = st.columns(2)

                    # -------------------- EDIT MEDICINE --------------------

                    with edit_col:

                        if st.button(
                            "Edit",
                            key=f"edit_{medicine_id}"
                        ):
                            st.session_state[f"editing_{medicine_id}"] = True

                    if st.session_state.get(f"editing_{medicine_id}", False):

                        with st.form(f"edit_form_{medicine_id}"):

                            new_name = st.text_input(
                                "Medicine Name",
                                value=medicine["medicine_name"]
                            )

                            new_type = st.selectbox(
                                "Medicine Type",
                                ["regular", "temporary"],
                                index=0 if medicine["medicine_type"] == "regular" else 1
                            )

                            new_dosage = st.text_input(
                                "Dosage",
                                value=medicine["dosage"] or ""
                            )

                            new_instructions = st.text_area(
                                "Instructions",
                                value=medicine["instructions"] or ""
                            )

                            old_times = get_dose_times(medicine_id)

                            new_frequency = st.selectbox(
                                "Doses per day",
                                [1, 2, 3, 4],
                                index=min(max(len(old_times), 1), 4) - 1
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

                                new_times.append(chosen_time.strftime("%H:%M"))

                            new_start = st.date_input(
                                "Start Date",
                                value=date.fromisoformat(medicine["start_date"]),
                                key=f"edit_start_{medicine_id}"
                            )

                            new_end = None

                            if new_type == "temporary":
                                default_end = (
                                    date.fromisoformat(medicine["end_date"])
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
                                value=float(medicine["refill_threshold"]),
                                step=1.0,
                                key=f"edit_threshold_{medicine_id}"
                            )

                            save = st.form_submit_button("Save Changes")

                            if save:

                                if not new_name.strip():
                                    st.error("Medicine name is required.")

                                elif new_end and new_end < new_start:
                                    st.error("End date cannot be before start date.")

                                else:
                                    update_medicine(
                                        medicine_id,
                                        user_id,
                                        new_name.strip(),
                                        new_type,
                                        new_dosage.strip(),
                                        new_instructions.strip(),
                                        new_start.isoformat(),
                                        new_end.isoformat() if new_end else None,
                                        new_times,
                                        new_stock,
                                        new_threshold
                                    )

                                    st.session_state[f"editing_{medicine_id}"] = False
                                    st.success("Medicine updated successfully!")
                                    st.rerun()

                    # -------------------- DELETE MEDICINE --------------------

                    with delete_col:

                        if st.button(
                            "Delete",
                            key=f"delete_{medicine_id}"
                        ):
                            st.session_state[f"deleting_{medicine_id}"] = True

                    if st.session_state.get(f"deleting_{medicine_id}", False):

                        st.warning("Are you sure you want to delete this medicine?")

                        confirm_col, cancel_col = st.columns(2)

                        with confirm_col:
                            if st.button(
                                "Confirm Delete",
                                key=f"confirm_delete_{medicine_id}"
                            ):
                                delete_medicine(medicine_id, user_id)
                                st.success("Medicine deleted.")
                                st.rerun()

                        with cancel_col:
                            if st.button(
                                "Cancel",
                                key=f"cancel_delete_{medicine_id}"
                            ):
                                st.session_state[f"deleting_{medicine_id}"] = False
                                st.rerun()
