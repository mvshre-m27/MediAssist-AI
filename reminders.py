
import streamlit as st
from datetime import date, datetime
from database import get_connection


# -------------------- MEDICINE REMINDERS --------------------

def get_due_reminders(user_id):
    """Get today's due and unconfirmed medicine doses."""

    today = date.today().isoformat()
    current_time = datetime.now().strftime("%H:%M")

    with get_connection() as conn:
        reminders = conn.execute("""
            SELECT
                ds.id AS schedule_id,
                ds.dose_time,
                m.medicine_name,
                m.dosage
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
                AND ds.dose_time <= ?
                AND (
                    dr.status IS NULL
                    OR dr.status = 'unconfirmed'
                )
            ORDER BY ds.dose_time
        """, (
            today,
            user_id,
            today,
            today,
            current_time
        )).fetchall()

    return reminders


def show_medicine_reminders(user_id):

    reminders = get_due_reminders(user_id)

    st.subheader("⏰ Medicine Reminders")

    if not reminders:
        st.success("No pending medicine reminders right now.")
        return

    for reminder in reminders:

        st.warning(
            f"Time for {reminder['medicine_name']} "
            f"({reminder['dosage'] or 'Dosage not specified'}) "
            f"- Scheduled at {reminder['dose_time']}"
        )


# -------------------- STOCK REFILL REMINDERS --------------------

def get_low_stock_medicines(user_id):
    """Get active medicines with stock at or below refill threshold."""

    today = date.today().isoformat()

    with get_connection() as conn:
        medicines = conn.execute("""
            SELECT
                id,
                medicine_name,
                remaining_stock,
                refill_threshold
            FROM medicines
            WHERE user_id = ?
                AND is_active = 1
                AND start_date <= ?
                AND (end_date IS NULL OR end_date >= ?)
                AND remaining_stock <= refill_threshold
            ORDER BY remaining_stock ASC
        """, (
            user_id,
            today,
            today
        )).fetchall()

    return medicines


def show_stock_reminders(user_id):

    medicines = get_low_stock_medicines(user_id)

    st.subheader("📦 Stock Refill Reminders")

    if not medicines:
        st.success("All your medicines have sufficient stock.")
        return

    for medicine in medicines:

        st.warning(
            f"Low stock: {medicine['medicine_name']} - "
            f"Only {medicine['remaining_stock']} remaining. "
            f"Refill threshold: {medicine['refill_threshold']}."
        )


# -------------------- MAIN REMINDERS PAGE --------------------

def show_reminders(user_id):

    st.title("🔔 Reminders")

    show_medicine_reminders(user_id)

    st.divider()

    show_stock_reminders(user_id)
