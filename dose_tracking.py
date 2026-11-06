
import streamlit as st
from datetime import date, datetime
from database import get_connection


# -------------------- DATABASE FUNCTIONS --------------------

def get_today_doses(user_id):
    """Get today's scheduled doses for the logged-in user."""

    today = date.today().isoformat()

    with get_connection() as conn:
        doses = conn.execute("""
            SELECT
                ds.id AS schedule_id,
                ds.dose_time,
                m.id AS medicine_id,
                m.medicine_name,
                m.dosage,
                m.start_date,
                m.end_date,
                m.remaining_stock,
                dr.status
            FROM dose_schedules ds
            JOIN medicines m
                ON ds.medicine_id = m.id
            LEFT JOIN dose_records dr
                ON ds.id = dr.schedule_id
                AND dr.scheduled_for = ?
            WHERE m.user_id = ?
                AND m.is_active = 1
                AND m.start_date <= ?
                AND (m.end_date IS NULL OR m.end_date >= ?)
            ORDER BY ds.dose_time
        """, (today, user_id, today, today)).fetchall()

    return doses


def save_dose_status(schedule_id, status, user_id):
    """Save a dose status and update stock safely."""

    allowed_statuses = ["taken", "missed", "unconfirmed"]

    if status not in allowed_statuses:
        return False

    today = date.today().isoformat()
    current_time = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:

        # Verify that this schedule belongs to the logged-in user.
        dose = conn.execute("""
            SELECT
                dr.status,
                m.id AS medicine_id,
                m.remaining_stock,
                m.total_stock
            FROM dose_schedules ds
            JOIN medicines m
                ON ds.medicine_id = m.id
            LEFT JOIN dose_records dr
                ON ds.id = dr.schedule_id
                AND dr.scheduled_for = ?
            WHERE ds.id = ?
                AND m.user_id = ?
        """, (today, schedule_id, user_id)).fetchone()

        if dose is None:
            return False

        old_status = dose["status"]

        # Do not record a dose as taken if no stock is available.
        if status == "taken" and old_status != "taken":

            if dose["remaining_stock"] <= 0:
                return False

            conn.execute("""
                UPDATE medicines
                SET remaining_stock = remaining_stock - 1
                WHERE id = ?
                    AND user_id = ?
                    AND remaining_stock > 0
            """, (dose["medicine_id"], user_id))

        # Restore one unit when changing Taken to another status.
        elif old_status == "taken" and status != "taken":

            conn.execute("""
                UPDATE medicines
                SET remaining_stock = MIN(
                    total_stock,
                    remaining_stock + 1
                )
                WHERE id = ?
                    AND user_id = ?
            """, (dose["medicine_id"], user_id))

        # Insert or update today's dose record.
        conn.execute("""
            INSERT INTO dose_records
                (schedule_id, scheduled_for, status, taken_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(schedule_id, scheduled_for)
            DO UPDATE SET
                status = excluded.status,
                taken_at = excluded.taken_at
        """, (
            schedule_id,
            today,
            status,
            current_time if status == "taken" else None
        ))

    return True


def reset_dose_status(schedule_id, user_id):
    """Reset a dose and restore stock if it was previously taken."""

    today = date.today().isoformat()

    with get_connection() as conn:

        # Verify ownership and get the existing dose status.
        dose = conn.execute("""
            SELECT
                dr.status,
                m.id AS medicine_id
            FROM dose_schedules ds
            JOIN medicines m
                ON ds.medicine_id = m.id
            LEFT JOIN dose_records dr
                ON ds.id = dr.schedule_id
                AND dr.scheduled_for = ?
            WHERE ds.id = ?
                AND m.user_id = ?
        """, (today, schedule_id, user_id)).fetchone()

        if dose is None:
            return False

        # Restore stock if the dose was previously marked Taken.
        if dose["status"] == "taken":

            conn.execute("""
                UPDATE medicines
                SET remaining_stock = MIN(
                    total_stock,
                    remaining_stock + 1
                )
                WHERE id = ?
                    AND user_id = ?
            """, (dose["medicine_id"], user_id))

        # Delete only this user's schedule record for today.
        conn.execute("""
            DELETE FROM dose_records
            WHERE schedule_id = ?
                AND scheduled_for = ?
                AND EXISTS (
                    SELECT 1
                    FROM dose_schedules ds
                    JOIN medicines m
                        ON ds.medicine_id = m.id
                    WHERE ds.id = dose_records.schedule_id
                        AND m.user_id = ?
                )
        """, (schedule_id, today, user_id))

    return True


# -------------------- DOSE TRACKING UI --------------------

def show_dose_tracking(user_id):

    st.title("💊 Daily Dose Tracking")
    st.write("Track your daily medicine intake.")

    doses = get_today_doses(user_id)

    if not doses:
        st.info("No medicine doses scheduled for today.")
        return

    today_display = date.today().strftime("%d %B %Y")
    st.subheader(f"Today's Schedule - {today_display}")

    for dose in doses:

        schedule_id = dose["schedule_id"]
        status = dose["status"] or "unconfirmed"
        remaining_stock = dose["remaining_stock"]

        with st.container(border=True):

            st.write(f"**{dose['medicine_name']}**")
            st.write(
                f"Dosage: {dose['dosage'] or 'Not specified'}"
            )
            st.write(f"Scheduled Time: {dose['dose_time']}")
            st.write(f"Remaining Stock: {remaining_stock}")

            if status == "taken":
                st.success("Dose Taken")

            elif status == "missed":
                st.error("Dose Missed")

            else:
                st.info("Dose Unconfirmed")

            if remaining_stock <= 0 and status != "taken":
                st.warning(
                    "No stock available. Update your medicine stock "
                    "before marking this dose as taken."
                )

            col1, col2, col3 = st.columns(3)

            # -------------------- TAKEN --------------------

            with col1:

                if st.button(
                    "Taken",
                    key=f"taken_{schedule_id}",
                    disabled=(
                        status == "taken" or remaining_stock <= 0
                    )
                ):

                    success = save_dose_status(
                        schedule_id,
                        "taken",
                        user_id
                    )

                    if success:
                        st.rerun()
                    else:
                        st.error(
                            "Unable to update dose. Please check stock."
                        )

            # -------------------- MISSED --------------------

            with col2:

                if st.button(
                    "Missed",
                    key=f"missed_{schedule_id}",
                    disabled=status == "missed"
                ):

                    success = save_dose_status(
                        schedule_id,
                        "missed",
                        user_id
                    )

                    if success:
                        st.rerun()
                    else:
                        st.error("Unable to update dose status.")

            # -------------------- RESET --------------------

            with col3:

                if st.button(
                    "Reset",
                    key=f"reset_{schedule_id}",
                    disabled=status == "unconfirmed"
                ):

                    success = reset_dose_status(
                        schedule_id,
                        user_id
                    )

                    if success:
                        st.rerun()
                    else:
                        st.error("Unable to reset this dose.")
