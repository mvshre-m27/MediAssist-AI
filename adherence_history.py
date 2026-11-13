
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

    return [dict(r) for r in records]


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


import altair as alt

# -------------------- ADHERENCE HISTORY PAGE --------------------

def show_adherence_history(user_id):
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>📊 Adherence Analytics & Trends</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>Longitudinal dose confirmation trends, compliance rates, and habit stability</p>
    </div>
    """, unsafe_allow_html=True)

    ctl1, ctl2 = st.columns([2, 1])
    with ctl1:
        period = st.radio(
            "Evaluation Window:",
            [7, 15, 30],
            format_func=lambda x: f"Last {x} Days",
            horizontal=True
        )

    records = get_adherence_data(user_id, period)
    total, taken, missed, unconfirmed, adherence = calculate_adherence(records)

    # Calculate streak from records
    dates_map = {}
    for r in records:
        d = r["scheduled_for"]
        if d not in dates_map:
            dates_map[d] = {"taken": 0, "missed": 0}
        if r["status"] == "taken":
            dates_map[d]["taken"] += 1
        elif r["status"] == "missed":
            dates_map[d]["missed"] += 1

    streak_days = 0
    for d in sorted(dates_map.keys(), reverse=True):
        day_data = dates_map[d]
        if day_data["taken"] > 0 and day_data["missed"] == 0:
            streak_days += 1
        elif day_data["missed"] > 0:
            break

    # Summary Metrics
    with st.container(border=True):
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Scheduled", total)
        m2.metric("Confirmed Taken", taken)
        m3.metric("Missed Doses", missed)
        m4.metric("Adherence Rate", f"{adherence:.1f}%")
        m5.metric("Active Streak", f"{streak_days} Days" if streak_days > 0 else "0 Days")

        # Clinical compliance indicator banner
        if (taken + missed) > 0:
            if adherence >= 80:
                tier_msg = "🟢 <b>Optimal Compliance (≥80%):</b> Excellent routine consistency. High adherence strongly correlates with reduced risk of chronic disease complications."
                border_col = "#10b981"
                bg_col = "#f0fdf4"
            else:
                tier_msg = "🟡 <b>Suboptimal Compliance (<80%):</b> Frequent missed doses elevate non-adherence risk. Consider reviewing dose timings or enabling supportive reminders."
                border_col = "#f59e0b"
                bg_col = "#fffbeb"

            st.markdown(
                f"<div style='background-color: {bg_col}; border-left: 4px solid {border_col}; padding: 10px 14px; border-radius: 6px; margin-top: 10px; font-size: 13.5px; color: #1e293b;'>"
                f"{tier_msg}</div>",
                unsafe_allow_html=True
            )

    if not records:
        st.info("No dose history recorded for this timeframe.")
        return

    # Visual Interactive Charts Section
    st.markdown("#### Dose Compliance Breakdown")

    # Aggregate records for Daily Timeline Chart
    daily_records = []
    for d in sorted(dates_map.keys()):
        # count unconfirmed for this day
        unconf = sum(1 for r in records if r["scheduled_for"] == d and r["status"] == "unconfirmed")
        if dates_map[d]["taken"] > 0:
            daily_records.append({"Date": d, "Status": "Taken", "Doses": dates_map[d]["taken"]})
        if dates_map[d]["missed"] > 0:
            daily_records.append({"Date": d, "Status": "Missed", "Doses": dates_map[d]["missed"]})
        if unconf > 0:
            daily_records.append({"Date": d, "Status": "Unconfirmed", "Doses": unconf})

    ch_col1, ch_col2 = st.columns([1.8, 1])

    with ch_col1:
        st.caption("Daily Dose Distribution Over Selected Window")
        if daily_records:
            df_daily = pd.DataFrame(daily_records)
            bar_chart = alt.Chart(df_daily).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X('Date:O', title='Date', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Doses:Q', title='Doses Count'),
                color=alt.Color('Status:N', scale=alt.Scale(
                    domain=['Taken', 'Missed', 'Unconfirmed'],
                    range=['#10b981', '#ef4444', '#f59e0b']
                )),
                tooltip=['Date', 'Status', 'Doses']
            ).properties(height=260)
            st.altair_chart(bar_chart, use_container_width=True)

    with ch_col2:
        st.caption("Proportion by Outcome")
        pie_data = []
        if taken > 0:
            pie_data.append({"Outcome": "Taken", "Count": taken})
        if missed > 0:
            pie_data.append({"Outcome": "Missed", "Count": missed})
        if unconfirmed > 0:
            pie_data.append({"Outcome": "Unconfirmed", "Count": unconfirmed})

        if pie_data:
            df_pie = pd.DataFrame(pie_data)
            donut = alt.Chart(df_pie).mark_arc(innerRadius=45).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Outcome", type="nominal", scale=alt.Scale(
                    domain=['Taken', 'Missed', 'Unconfirmed'],
                    range=['#10b981', '#ef4444', '#f59e0b']
                )),
                tooltip=['Outcome', 'Count']
            ).properties(height=260)
            st.altair_chart(donut, use_container_width=True)

    # Detailed Searchable History Table
    st.markdown("#### Dose Log Audit")
    
    t_f1, t_f2 = st.columns([2, 1])
    with t_f1:
        search_med = st.text_input("Search by Medicine Name", placeholder="Filter by medicine...", label_visibility="collapsed")
    with t_f2:
        filter_status = st.selectbox("Filter Status", ["All Statuses", "Taken", "Missed", "Unconfirmed"], label_visibility="collapsed")

    filtered_history = []
    for r in records:
        med_match = search_med.lower() in r["medicine_name"].lower() if search_med else True
        stat_cap = r["status"].capitalize()
        status_match = True if filter_status == "All Statuses" else (stat_cap == filter_status)

        if med_match and status_match:
            filtered_history.append({
                "Date": r["scheduled_for"],
                "Medicine": r["medicine_name"],
                "Dosage": r["dosage"] or "-",
                "Scheduled Time": r["dose_time"],
                "Status": stat_cap,
                "Confirmed At": r["taken_at"].split("T")[-1][:5] if r.get("taken_at") else "-"
            })

    if filtered_history:
        st.dataframe(pd.DataFrame(filtered_history), width="stretch", hide_index=True)
    else:
        st.caption("No matching records found for the filter criteria.")
