
import streamlit as st
from datetime import date, datetime
from database import get_connection


# -------------------- DATABASE FUNCTIONS --------------------

def get_today_doses(user_id):
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


def save_dose_status(schedule_id, status):
    today = date.today().isoformat()
    current_time = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:

        # Get the existing dose status and medicine stock
        dose = conn.execute("""
            SELECT dr.status, m.id AS medicine_id,
                   m.remaining_stock, m.total_stock
            FROM dose_schedules ds
            JOIN medicines m ON ds.medicine_id = m.id
            LEFT JOIN dose_records dr
                ON ds.id = dr.schedule_id
                AND dr.scheduled_for = ?
            WHERE ds.id = ?
        """, (today, schedule_id)).fetchone()

        if dose is None:
            return

        old_status = dose["status"]

        # Deduct stock when changing to Taken
        if status == "taken" and old_status != "taken":
            conn.execute("""
                UPDATE medicines
                SET remaining_stock = MAX(0, remaining_stock - 1)
                WHERE id = ?
            """, (dose["medicine_id"],))

        # Restore stock if changing Taken to another status
        elif old_status == "taken" and status != "taken":
            conn.execute("""
                UPDATE medicines
                SET remaining_stock = MIN(total_stock, remaining_stock + 1)
                WHERE id = ?
            """, (dose["medicine_id"],))

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

# -------------------- DOSE TRACKING UI --------------------

def show_dose_tracking(user_id):

    st.title("💊 Daily Dose Tracking")
    st.write("Track your daily medicine intake.")

    doses = get_today_doses(user_id)

    if not doses:
        st.info("No medicine doses scheduled for today.")
        return

    today = date.today().strftime("%d %B %Y")
    st.subheader(f"Today's Schedule - {today}")

    for dose in doses:

        schedule_id = dose["schedule_id"]
        status = dose["status"] or "unconfirmed"

        with st.container(border=True):

            st.write(f"**{dose['medicine_name']}**")
            st.write(f"Dosage: {dose['dosage'] or 'Not specified'}")
            st.write(f"Scheduled Time: {dose['dose_time']}")

            if status == "taken":
                st.success("Dose Taken")

            elif status == "missed":
                st.error("Dose Missed")

            else:
                st.info("Dose Unconfirmed")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "Taken",
                    key=f"taken_{schedule_id}",
                    disabled=status == "taken"
                ):
                    save_dose_status(schedule_id, "taken")
                    st.rerun()

            with col2:
                if st.button(
                    "Missed",
                    key=f"missed_{schedule_id}",
                    disabled=status == "missed"
                ):
                    save_dose_status(schedule_id, "missed")
                    st.rerun()

            with col3:
                if st.button(
                    "Reset",
                    key=f"reset_{schedule_id}",
                    disabled=status == "unconfirmed"
                ):
                    today = date.today().isoformat()

                    with get_connection() as conn:
                        conn.execute("""
                            DELETE FROM dose_records
                            WHERE schedule_id = ?
                            AND scheduled_for = ?
                        """, (schedule_id, today))

                    st.rerun()
