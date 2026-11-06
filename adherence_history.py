
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database import get_connection


# -------------------- FETCH ADHERENCE DATA --------------------

def get_adherence_data(user_id, days=7):
    """Fetch due dose history for the logged-in user."""

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    today = date.today().isoformat()
    current_time = datetime.now().strftime("%H:%M")

    with get_connection() as conn:

        records = conn.execute("""
            WITH RECURSIVE dates(scheduled_for) AS (
                SELECT ?
                UNION ALL
                SELECT date(scheduled_for, '+1 day')
                FROM dates
                WHERE scheduled_for < ?
            )

            SELECT
                dates.scheduled_for,
                COALESCE(dr.status, 'unconfirmed') AS status,
                dr.taken_at,
                ds.dose_time,
                m.medicine_name,
                m.dosage

            FROM dates

            JOIN medicines m
                ON m.user_id = ?
                AND m.is_active = 1
                AND dates.scheduled_for >= m.start_date
                AND (
                    m.end_date IS NULL
                    OR dates.scheduled_for <= m.end_date
                )

            JOIN dose_schedules ds
                ON ds.medicine_id = m.id

            LEFT JOIN dose_records dr
                ON dr.schedule_id = ds.id
                AND dr.scheduled_for = dates.scheduled_for

            WHERE (
                dates.scheduled_for < ?
                OR ds.dose_time <= ?
            )

            ORDER BY
                dates.scheduled_for DESC,
                ds.dose_time DESC

        """, (
            start_date.isoformat(),
            end_date.isoformat(),
            user_id,
            today,
            current_time
        )).fetchall()

    return records


# -------------------- CALCULATE ADHERENCE --------------------

def calculate_adherence(records):
    """Calculate adherence using only confirmed dose outcomes."""

    total = len(records)

    taken = sum(
        1 for record in records
        if record["status"] == "taken"
    )

    missed = sum(
        1 for record in records
        if record["status"] == "missed"
    )

    unconfirmed = sum(
        1 for record in records
        if record["status"] == "unconfirmed"
    )

    # Unconfirmed doses are excluded from the adherence denominator.
    confirmed = taken + missed

    adherence = (
        taken / confirmed * 100
        if confirmed > 0
        else 0
    )

    return total, taken, missed, unconfirmed, adherence


# -------------------- ADHERENCE HISTORY PAGE --------------------

def show_adherence_history(user_id):

    st.title("📊 Adherence History")

    st.write(
        "View your medicine intake and adherence progress."
    )

    period = st.selectbox(
        "Select Time Period",
        [7, 15, 30],
        format_func=lambda x: f"Last {x} days"
    )

    records = get_adherence_data(user_id, period)

    total, taken, missed, unconfirmed, adherence = (
        calculate_adherence(records)
    )

    st.subheader("Adherence Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Due", total)
    col2.metric("Taken", taken)
    col3.metric("Missed", missed)
    col4.metric("Adherence", f"{adherence:.1f}%")

    st.progress(adherence / 100)

    st.write(f"Unconfirmed doses: {unconfirmed}")

    st.caption(
        "Adherence is calculated from confirmed doses only "
        "(Taken + Missed). Unconfirmed doses are excluded."
    )

    st.divider()

    st.subheader("Dose History")

    if not records:

        st.info(
            "No dose history available for this period."
        )

    else:

        history = []

        for record in records:

            history.append({
                "Date": record["scheduled_for"],
                "Medicine": record["medicine_name"],
                "Dosage": record["dosage"] or "Not specified",
                "Scheduled Time": record["dose_time"],
                "Status": record["status"].capitalize(),
                "Taken At": record["taken_at"] or "-"
            })

        df = pd.DataFrame(history)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
