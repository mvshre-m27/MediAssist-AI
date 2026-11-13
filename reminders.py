
import streamlit as st
from datetime import date, datetime
from database import get_connection
from dose_tracking import save_dose_status
from medicines import refill_medicine_stock


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

    return [dict(r) for r in reminders]


def get_low_stock_medicines(user_id):
    """Get active medicines with stock at or below refill threshold."""
    today = date.today().isoformat()
    with get_connection() as conn:
        medicines = conn.execute("""
            SELECT
                id,
                medicine_name,
                remaining_stock,
                total_stock,
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

    return [dict(m) for m in medicines]


# -------------------- MAIN REMINDERS PAGE --------------------

def show_medicine_reminders(user_id):
    reminders = get_due_reminders(user_id)

    st.markdown("#### ⏰ Pending Due Dose Reminders")

    if not reminders:
        st.success("✅ All scheduled doses up to the current hour have been confirmed.")
        return

    for reminder in reminders:
        with st.container(border=True):
            r_col1, r_col2 = st.columns([3, 1])
            with r_col1:
                st.markdown(f"**💊 {reminder['medicine_name']}** &bull; `{reminder['dosage'] or 'Standard dose'}`")
                st.caption(f"Scheduled at **{reminder['dose_time']}** &bull; Status: Due / Unconfirmed")
            with r_col2:
                st.markdown(f"<div style='text-align: right; margin-bottom: 6px;'><span class='badge-pill badge-amber'>⏰ Due Now</span></div>", unsafe_allow_html=True)
                if st.button("Mark Taken", key=f"rem_taken_{reminder['schedule_id']}", type="primary", use_container_width=True):
                    success = save_dose_status(reminder['schedule_id'], "taken", user_id)
                    if success:
                        st.success(f"Confirmed {reminder['medicine_name']} taken!")
                        st.rerun()
                    else:
                        st.error("Check stock before marking taken.")


def show_stock_reminders(user_id):
    medicines = get_low_stock_medicines(user_id)

    st.markdown("#### 📦 Medication Stock & Refill Alerts")

    if not medicines:
        st.success("✅ All active medications maintain sufficient inventory above refill thresholds.")
        return

    for medicine in medicines:
        rem = medicine["remaining_stock"]
        thresh = medicine["refill_threshold"]
        badge_cls = "badge-red" if rem <= 0 else "badge-amber"
        stat_text = "DEPLETED" if rem <= 0 else "LOW STOCK"

        with st.container(border=True):
            s_col1, s_col2 = st.columns([3, 1])
            with s_col1:
                st.markdown(f"**💊 {medicine['medicine_name']}**")
                st.caption(f"Remaining: **{rem} units** (Threshold: {thresh} units)")
            with s_col2:
                st.markdown(f"<div style='text-align: right; margin-bottom: 6px;'><span class='badge-pill {badge_cls}'>{stat_text}</span></div>", unsafe_allow_html=True)
                if st.button("➕ Quick Refill (+30)", key=f"rem_refill_{medicine['id']}", use_container_width=True):
                    refill_medicine_stock(medicine['id'], user_id, 30)
                    st.success(f"Added +30 units to {medicine['medicine_name']}!")
                    st.rerun()


def show_reminders(user_id):
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>🔔 Active Reminders & Refill Alerts</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>Real-time notifications for due medication doses and low-stock refills</p>
    </div>
    """, unsafe_allow_html=True)

    show_medicine_reminders(user_id)
    st.divider()
    show_stock_reminders(user_id)
