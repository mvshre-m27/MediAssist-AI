
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
                m.instructions,
                m.start_date,
                m.end_date,
                m.remaining_stock,
                m.total_stock,
                m.refill_threshold,
                dr.status,
                dr.taken_at
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

    return [dict(d) for d in doses]


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
    today_display = date.today().strftime("%A, %d %B %Y")
    
    st.markdown(f"""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>💊 Daily Dose Tracking</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>{today_display} &bull; Confirm intake and track remaining inventory</p>
    </div>
    """, unsafe_allow_html=True)

    doses = get_today_doses(user_id)

    if not doses:
        st.info("No medicine doses scheduled for today. Add active medicines in the **Medicines** tab.")
        return

    # Aggregate counts
    total_doses = len(doses)
    taken_doses = sum(1 for d in doses if d["status"] == "taken")
    missed_doses = sum(1 for d in doses if d["status"] == "missed")
    pending_doses = total_doses - (taken_doses + missed_doses)
    progress_pct = (taken_doses / total_doses * 100) if total_doses > 0 else 100

    # Header Progress Banner
    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Scheduled", total_doses)
        m2.metric("Confirmed Taken", taken_doses)
        m3.metric("Missed", missed_doses)
        m4.metric("Pending / Due", pending_doses)

        st.progress(progress_pct / 100)
        
        if total_doses > 0 and taken_doses == total_doses:
            st.success("🎉 All scheduled doses for today have been confirmed! Excellent consistency.")
            if st.session_state.get("_trigger_balloons"):
                st.balloons()
                st.session_state["_trigger_balloons"] = False

    # Filter Tabs
    tab_all, tab_pending, tab_taken, tab_missed = st.tabs([
        f"All Doses ({total_doses})",
        f"Pending ({pending_doses})",
        f"Taken ({taken_doses})",
        f"Missed ({missed_doses})"
    ])

    tab_map = {
        "all": (tab_all, doses),
        "pending": (tab_pending, [d for d in doses if (d["status"] or "unconfirmed") == "unconfirmed"]),
        "taken": (tab_taken, [d for d in doses if d["status"] == "taken"]),
        "missed": (tab_missed, [d for d in doses if d["status"] == "missed"])
    }

    for key, (tab_obj, tab_doses) in tab_map.items():
        with tab_obj:
            if not tab_doses:
                st.caption(f"No doses in this category.")
                continue

            for dose in tab_doses:
                schedule_id = dose["schedule_id"]
                status = dose["status"] or "unconfirmed"
                remaining_stock = dose["remaining_stock"]
                total_stock = dose.get("total_stock", 30) or 30
                refill_thresh = dose.get("refill_threshold", 7) or 7
                dose_time_str = dose["dose_time"]

                # Determine time-of-day slot
                try:
                    hour_val = int(dose_time_str.split(":")[0])
                    if hour_val < 12:
                        slot_label = f"🌅 Morning ({dose_time_str})"
                        slot_class = "badge-blue"
                    elif hour_val < 17:
                        slot_label = f"☀️ Afternoon ({dose_time_str})"
                        slot_class = "badge-amber"
                    elif hour_val < 21:
                        slot_label = f"🌆 Evening ({dose_time_str})"
                        slot_class = "badge-purple"
                    else:
                        slot_label = f"🌙 Bedtime ({dose_time_str})"
                        slot_class = "badge-slate"
                except Exception:
                    slot_label = f"⏰ {dose_time_str}"
                    slot_class = "badge-slate"

                # Status Pill
                if status == "taken":
                    time_taken_str = f" at {dose['taken_at'].split('T')[-1][:5]}" if dose.get("taken_at") else ""
                    status_pill = f"<span class='badge-pill badge-green'>✓ Taken{time_taken_str}</span>"
                elif status == "missed":
                    status_pill = "<span class='badge-pill badge-red'>✕ Missed</span>"
                else:
                    status_pill = "<span class='badge-pill badge-amber'>⏳ Due / Pending</span>"

                # Stock Pill
                if remaining_stock <= refill_thresh:
                    stock_pill = f"<span class='badge-pill badge-red'>⚠️ Low Stock ({remaining_stock} left)</span>"
                else:
                    stock_pill = f"<span class='badge-pill badge-slate'>📦 Stock: {remaining_stock}</span>"

                with st.container(border=True):
                    # Card Header
                    hdr_col1, hdr_col2 = st.columns([3, 2])
                    with hdr_col1:
                        dosage_text = f" &bull; {dose['dosage']}" if dose.get("dosage") else ""
                        st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #0f172a;'>💊 {dose['medicine_name']} <span style='font-size: 13px; font-weight: 500; color: #64748b;'>{dosage_text}</span></div>", unsafe_allow_html=True)
                        if dose.get("instructions"):
                            st.caption(f"🍽️ {dose['instructions']}")
                    with hdr_col2:
                        st.markdown(f"<div style='text-align: right; display: flex; gap: 6px; justify-content: flex-end; align-items: center; flex-wrap: wrap;'><span class='badge-pill {slot_class}'>{slot_label}</span> {stock_pill} {status_pill}</div>", unsafe_allow_html=True)

                    if remaining_stock <= 0 and status != "taken":
                        st.warning("⚠️ Zero stock available. Please update medication inventory to confirm this dose.")

                    # Action Buttons
                    b1, b2, b3 = st.columns([1.2, 1.2, 1])

                    with b1:
                        if st.button("Mark Taken", key=f"taken_{schedule_id}_{key}", type="primary" if status != "taken" else "secondary", disabled=(status == "taken" or remaining_stock <= 0), use_container_width=True):
                            success = save_dose_status(schedule_id, "taken", user_id)
                            if success:
                                if (taken_doses + 1) == total_doses:
                                    st.session_state["_trigger_balloons"] = True
                                st.rerun()
                            else:
                                st.error("Stock depleted. Unable to mark taken.")

                    with b2:
                        if st.button("Mark Missed", key=f"missed_{schedule_id}_{key}", disabled=(status == "missed"), use_container_width=True):
                            success = save_dose_status(schedule_id, "missed", user_id)
                            if success:
                                st.rerun()
                            else:
                                st.error("Unable to update dose.")

                    with b3:
                        if st.button("Reset", key=f"reset_{schedule_id}_{key}", disabled=(status == "unconfirmed"), use_container_width=True):
                            success = reset_dose_status(schedule_id, user_id)
                            if success:
                                st.rerun()
                            else:
                                st.error("Unable to reset.")
