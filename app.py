
import streamlit as st
from datetime import date

from auth import create_user, verify_user
from database import (
    get_connection,
    get_user_comorbidities,
    save_user_comorbidities,
    KNOWN_COMORBIDITY_LABELS
)

from medicines import show_medicines
from dose_tracking import show_dose_tracking
from reminders import show_reminders
from adherence_history import show_adherence_history, get_adherence_data, calculate_adherence
from adherence_risk import show_adherence_risk_page
from food_suggestions import show_food_suggestions_page
from ddi_checker import show_ddi_checker_page
import ddi_engine as ddi


# =========================================
# 1. PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="MediAssist",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================
# 2. SESSION MANAGEMENT
# =========================================

if "user" not in st.session_state:
    st.session_state.user = None


# =========================================
# 3. CUSTOM DESIGN SYSTEM & CSS
# =========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
    background-color: #f8fafc;
}

/* Page container */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1200px;
}

/* Modern Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    letter-spacing: -0.02em;
}

.main-title {
    text-align: center;
    color: #065f46;
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 15px;
    font-weight: 500;
    margin-bottom: 24px;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.25rem !important;
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
}

/* Sidebar Navigation Items */
[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 3px !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
    margin: 1px 0 !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    border: 1px solid transparent !important;
    width: 100% !important;
}

/* Hide default circle radio dots */
[data-testid="stSidebar"] div[data-testid="stRadio"] label input[type="radio"],
[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {
    display: none !important;
}

/* Nav Typography */
[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    letter-spacing: -0.01em !important;
    margin: 0 !important;
}

/* Hover state */
[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background-color: #f8fafc !important;
    border-color: #e2e8f0 !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
    color: #0f172a !important;
}

/* Active Selected state - Modern Clinical Teal/Emerald Pill */
[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%) !important;
    border: 1px solid #a7f3d0 !important;
    box-shadow: 0 1px 3px rgba(5, 150, 105, 0.08) !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
    color: #065f46 !important;
    font-weight: 700 !important;
}

/* Elevated Metric Widgets */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    border-top: 3px solid #10b981;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.07);
}
div[data-testid="stMetric"] label {
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}

/* Containers with border */
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"][border="true"] {
    background: #ffffff;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 18px !important;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}

/* Buttons */
div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.88rem;
    min-height: 40px;
    transition: all 0.15s ease-in-out;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    color: #ffffff;
    border: none;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #047857 0%, #065f46 100%);
    box-shadow: 0 6px 16px rgba(5, 150, 105, 0.35);
    transform: translateY(-1px);
}
div.stButton > button[kind="secondary"] {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #334155;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #10b981;
    color: #059669;
    background: #f0fdf4;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    color: #475569 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #059669 !important;
    border-bottom-color: #059669 !important;
    border-bottom-width: 3px !important;
}

/* Modern Pill Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.badge-green { background: #dcfce7; color: #15803d; }
.badge-red { background: #fee2e2; color: #b91c1c; }
.badge-amber { background: #fef3c7; color: #b45309; }
.badge-blue { background: #e0f2fe; color: #0369a1; }
.badge-purple { background: #f3e8ff; color: #7e22ce; }
.badge-slate { background: #f1f5f9; color: #475569; }

/* Custom Action Cards */
.action-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    transition: all 0.2s ease;
    height: 100%;
}
.action-card:hover {
    border-color: #10b981;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.1);
    transform: translateY(-2px);
}

/* Dataframe clean borders */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================
# 4. PROFILE & DASHBOARD DATABASE FUNCTIONS
# =========================================

def get_home_dashboard_data(user_id):
    """Fetch live metrics and recent dose events for the Home dashboard."""
    today = date.today().isoformat()
    with get_connection() as conn:
        active_meds = conn.execute("""
            SELECT COUNT(*) as count
            FROM medicines
            WHERE user_id = ? AND is_active = 1
        """, (user_id,)).fetchone()["count"]

        # Today's total scheduled doses & status
        today_schedules = conn.execute("""
            SELECT ds.id, dr.status
            FROM dose_schedules ds
            JOIN medicines m ON ds.medicine_id = m.id
            LEFT JOIN dose_records dr ON ds.id = dr.schedule_id AND dr.scheduled_for = ?
            WHERE m.user_id = ?
              AND m.is_active = 1
              AND m.start_date <= ?
              AND (m.end_date IS NULL OR m.end_date >= ?)
        """, (today, user_id, today, today)).fetchall()

        today_doses = len(today_schedules)
        today_taken = sum(1 for r in today_schedules if r["status"] == "taken")
        today_missed = sum(1 for r in today_schedules if r["status"] == "missed")
        today_pending = max(0, today_doses - (today_taken + today_missed))

        low_stock_count = conn.execute("""
            SELECT COUNT(*) as count
            FROM medicines
            WHERE user_id = ? AND is_active = 1
              AND remaining_stock <= refill_threshold
        """, (user_id,)).fetchone()["count"]

        recent_activity = conn.execute("""
            SELECT
                dr.scheduled_for,
                COALESCE(dr.status, 'unconfirmed') AS status,
                dr.taken_at,
                ds.dose_time,
                m.medicine_name,
                m.dosage
            FROM dose_records dr
            JOIN dose_schedules ds ON dr.schedule_id = ds.id
            JOIN medicines m ON ds.medicine_id = m.id
            WHERE m.user_id = ?
            ORDER BY dr.scheduled_for DESC, ds.dose_time DESC
            LIMIT 5
        """, (user_id,)).fetchall()

    records_15 = get_adherence_data(user_id, days=15)
    adherence_pct = "No history"
    streak_days = 0
    if records_15:
        total, taken, missed, unconfirmed, adherence = calculate_adherence(records_15)
        if (taken + missed) > 0:
            adherence_pct = f"{adherence:.0f}%"
        else:
            adherence_pct = "Pending"

        dates_map = {}
        for r in records_15:
            d = r["scheduled_for"]
            if d not in dates_map:
                dates_map[d] = {"taken": 0, "missed": 0}
            if r["status"] == "taken":
                dates_map[d]["taken"] += 1
            elif r["status"] == "missed":
                dates_map[d]["missed"] += 1

        for d in sorted(dates_map.keys(), reverse=True):
            day_data = dates_map[d]
            if day_data["taken"] > 0 and day_data["missed"] == 0:
                streak_days += 1
            elif day_data["missed"] > 0:
                break

    return {
        "active_meds": active_meds,
        "today_doses": today_doses,
        "today_taken": today_taken,
        "today_missed": today_missed,
        "today_pending": today_pending,
        "today_progress": (today_taken / today_doses * 100) if today_doses > 0 else 100,
        "low_stock_count": low_stock_count,
        "streak_days": streak_days,
        "adherence_pct": adherence_pct,
        "recent_activity": [dict(r) for r in recent_activity]
    }


def get_profile_data(user_id):

    with get_connection() as conn:

        profile = conn.execute("""
            SELECT full_name, age
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        food = conn.execute("""
            SELECT diet_type, allergies,
                   dietary_restrictions, food_preferences
            FROM food_preferences
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return profile, food


def save_profile_data(
    user_id,
    full_name,
    age,
    diet_type,
    allergies,
    restrictions,
    food_preferences
):

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO user_profiles (
                user_id, full_name, age
            )
            VALUES (?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                full_name = excluded.full_name,
                age = excluded.age
        """, (
            user_id,
            full_name,
            age
        ))

        conn.execute("""
            INSERT INTO food_preferences (
                user_id,
                diet_type,
                allergies,
                dietary_restrictions,
                food_preferences
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                diet_type = excluded.diet_type,
                allergies = excluded.allergies,
                dietary_restrictions = excluded.dietary_restrictions,
                food_preferences = excluded.food_preferences
        """, (
            user_id,
            diet_type,
            allergies,
            restrictions,
            food_preferences
        ))


# =========================================
# 5. LOGIN AND REGISTRATION
# =========================================

def show_authentication():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown(
            '<div class="main-title">💚 MediAssist</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="subtitle">Clinical Medication Management & Dietary Intelligence</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):
            login_tab, register_tab = st.tabs(["Secure Login", "Create Account"])

            with login_tab:
                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="e.g. demo_patient")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                    if submitted:
                        if not username.strip() or not password:
                            st.error("Please enter both username and password.")
                        else:
                            user = verify_user(username, password)
                            if user:
                                st.session_state.user = user
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid username or password.")

                st.caption("💡 **Quick Demo Access:** Username `demo_patient` &bull; Password `Demo@12345`")

            with register_tab:
                with st.form("register_form"):
                    new_username = st.text_input("Choose a username")
                    new_password = st.text_input("Create password", type="password")
                    confirm_password = st.text_input("Confirm password", type="password")
                    registered = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                    if registered:
                        if not new_username.strip():
                            st.error("Please enter a username.")
                        elif not new_password:
                            st.error("Please enter a password.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            success, message, user_id = create_user(new_username, new_password)
                            if success:
                                st.success(message)
                                st.info("Account created! You can now log in.")
                            else:
                                st.error(message)


# =========================================
# 6. USER PROFILE PAGE
# =========================================

def show_profile(user):

    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>👤 Patient Profile & Clinical Health Record</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>Personal demographics, diagnosed comorbidities, and dietary restrictions</p>
    </div>
    """, unsafe_allow_html=True)

    try:

        profile, food = get_profile_data(user["id"])

        full_name = profile["full_name"] if profile else ""
        age = profile["age"] if profile else None

        diet_type = food["diet_type"] if food else None
        allergies = food["allergies"] if food else ""
        restrictions = (
            food["dietary_restrictions"] if food else ""
        )
        food_preferences = (
            food["food_preferences"] if food else ""
        )

        diet_options = [
            "Not specified",
            "Vegetarian",
            "Non-vegetarian",
            "Eggetarian",
            "Vegan",
            "Pescatarian"
        ]

        selected_diet = (
            diet_type if diet_type in diet_options
            else "Not specified"
        )

        st.subheader("Personal Information")

        with st.form("profile_form"):

            name_input = st.text_input(
                "Full Name",
                value=full_name or "",
                placeholder="Enter your full name"
            )

            age_input = st.text_input(
                "Age",
                value=str(age) if age is not None else "",
                placeholder="Enter your age"
            )

            st.divider()

            st.subheader("🏥 Diagnosed Chronic Health Conditions & Comorbidities")
            st.caption("Select your diagnosed medical conditions so MediAssist can tailor dietary harmonization and check for drug-disease contraindications.")

            existing_comorbs = get_user_comorbidities(user["id"])
            existing_keys = [c["condition_key"] for c in existing_comorbs]

            condition_options = list(KNOWN_COMORBIDITY_LABELS.keys())
            selected_conditions = st.multiselect(
                "Diagnosed Conditions:",
                options=condition_options,
                default=[k for k in existing_keys if k in condition_options],
                format_func=lambda x: KNOWN_COMORBIDITY_LABELS.get(x, x.title())
            )

            st.divider()

            st.subheader("Food Preferences")

            diet_input = st.selectbox(
                "Diet Type",
                diet_options,
                index=diet_options.index(selected_diet)
            )

            allergy_input = st.text_area(
                "Food Allergies",
                value=allergies or "",
                placeholder="Example: Peanuts, dairy, etc."
            )

            restriction_input = st.text_area(
                "Dietary Restrictions",
                value=restrictions or "",
                placeholder="Example: Low-sugar, low-sodium, etc."
            )

            preference_input = st.text_area(
                "Food Preferences",
                value=food_preferences or "",
                placeholder="Enter foods you prefer or avoid."
            )

            saved = st.form_submit_button(
                "Save Profile",
                use_container_width=True
            )

            if saved:

                age_value = None

                if age_input.strip():

                    try:
                        age_value = int(age_input)

                        if age_value < 1 or age_value > 120:
                            st.error(
                                "Please enter a valid age between 1 and 120."
                            )
                            return

                    except ValueError:
                        st.error("Age must be a whole number.")
                        return

                try:

                    save_profile_data(
                        user["id"],
                        name_input.strip(),
                        age_value,
                        None if diet_input == "Not specified" else diet_input,
                        allergy_input.strip(),
                        restriction_input.strip(),
                        preference_input.strip()
                    )

                    save_user_comorbidities(user["id"], selected_conditions)

                    st.success(
                        "Your profile and medical conditions have been saved successfully!"
                    )

                except Exception as e:

                    st.error(f"Unable to save profile: {e}")

    except Exception as e:

        st.error(f"Unable to load profile: {e}")


# =========================================
# 7. SETTINGS PAGE
# =========================================

def show_settings(user_id):
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <h1 style='font-size: 26px; margin: 0;'>⚙️ Application Settings & Safeguards</h1>
        <p style='color: #64748b; margin: 4px 0 0 0; font-size: 14px;'>Configure supportive adherence interventions, caregiver notifications, and safety thresholds</p>
    </div>
    """, unsafe_allow_html=True)

    with get_connection() as conn:
        pref = conn.execute("""
            SELECT gentle_reminders_enabled, caregiver_alerts_enabled, alert_threshold
            FROM intervention_preferences
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        caregivers = conn.execute("""
            SELECT id, caregiver_name, relationship, contact_method, contact_value, consent_given, is_enabled
            FROM caregiver_contacts
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()

        logs = conn.execute("""
            SELECT intervention_type, delivery_status, message, created_at
            FROM intervention_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,)).fetchall()

    # 1. Intervention Preferences
    st.subheader("🔔 Supportive Adherence Interventions")
    st.caption("Control when and how MediAssist provides proactive adherence check-ins.")

    gentle_default = bool(pref["gentle_reminders_enabled"]) if pref else False
    caregiver_default = bool(pref["caregiver_alerts_enabled"]) if pref else False
    threshold_default = pref["alert_threshold"] if pref else "high"

    with st.form("intervention_pref_form"):
        gentle_val = st.toggle("Enable Gentle In-App Reminders when Adherence Risk is Elevated", value=gentle_default)
        caregiver_val = st.toggle("Enable Optional Caregiver Alert Notifications", value=caregiver_default)
        threshold_options = ["high", "medium"]
        threshold_idx = 0 if threshold_default == "high" else 1
        threshold_val = st.selectbox(
            "Risk Threshold to Trigger Interventions",
            threshold_options,
            index=threshold_idx,
            format_func=lambda x: "High Risk Only (Recommended)" if x == "high" else "Medium or High Risk"
        )

        saved_pref = st.form_submit_button("Save Notification Settings", use_container_width=True)
        if saved_pref:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO intervention_preferences (user_id, gentle_reminders_enabled, caregiver_alerts_enabled, alert_threshold)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        gentle_reminders_enabled = excluded.gentle_reminders_enabled,
                        caregiver_alerts_enabled = excluded.caregiver_alerts_enabled,
                        alert_threshold = excluded.alert_threshold,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, int(gentle_val), int(caregiver_val), threshold_val))
            st.success("Intervention settings saved successfully!")
            st.rerun()

    st.divider()

    # 2. Caregiver Contact Form
    st.subheader("👥 Caregiver Contacts")
    st.caption("A trusted family member or caregiver who can support your medication routine.")

    if caregivers:
        for cg in caregivers:
            status_text = "Active" if cg["is_enabled"] else "Disabled"
            consent_text = "Consent Verified" if cg["consent_given"] else "Consent Pending"
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{cg['caregiver_name']}** ({cg['relationship'] or 'Caregiver'})")
                    st.caption(f"Contact: {cg['contact_method'].upper()} — `{cg['contact_value']}` | {consent_text}")
                with col2:
                    st.write(f"Status: **{status_text}**")
    else:
        st.info("No caregiver contact added yet.")

    with st.expander("➕ Add New Caregiver Contact"):
        with st.form("caregiver_form"):
            cg_name = st.text_input("Caregiver Name")
            cg_rel = st.text_input("Relationship", placeholder="e.g. Spouse, Adult Child, Guardian")
            cg_method = st.selectbox("Preferred Contact Method", ["email", "phone"])
            cg_val = st.text_input("Contact Info (Email or Phone Number)")
            cg_consent = st.checkbox("I confirm that the caregiver has consented to receive medication safety notifications.")

            submitted_cg = st.form_submit_button("Save Caregiver Contact", use_container_width=True)
            if submitted_cg:
                if not cg_name.strip() or not cg_val.strip():
                    st.error("Please provide both name and contact information.")
                else:
                    with get_connection() as conn:
                        conn.execute("""
                            INSERT INTO caregiver_contacts (user_id, caregiver_name, relationship, contact_method, contact_value, consent_given, is_enabled)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (user_id, cg_name.strip(), cg_rel.strip(), cg_method, cg_val.strip(), int(cg_consent), 1))
                    st.success("Caregiver contact added!")
                    st.rerun()

    st.divider()

    # 3. Audit Logs
    st.subheader("📜 Intervention Delivery Logs")
    if logs:
        for log in logs:
            st.text(f"[{log['created_at']}] ({log['delivery_status'].upper()}) {log['intervention_type']}: {log['message']}")
    else:
        st.caption("No intervention events logged yet.")


# =========================================
# 8. MAIN DASHBOARD
# =========================================

def show_dashboard():

    user = st.session_state.user

    # -------------------------------------
    # SIDEBAR - MEDICAL AI DASHBOARD
    # -------------------------------------

    # Navigation State
    if "nav_page" not in st.session_state or not st.session_state.nav_page:
        st.session_state.nav_page = "Home"

    # Fetch live indicators & patient profile
    today_iso = date.today().isoformat()
    with get_connection() as conn:
        p_row = conn.execute("SELECT full_name FROM user_profiles WHERE user_id = ?", (user["id"],)).fetchone()
        display_name = p_row["full_name"] if p_row and p_row["full_name"] else user["username"]

        active_meds_count = conn.execute(
            "SELECT COUNT(*) as count FROM medicines WHERE user_id = ? AND is_active = 1",
            (user["id"],)
        ).fetchone()["count"]

        low_stock_count = conn.execute(
            "SELECT COUNT(*) as count FROM medicines WHERE user_id = ? AND is_active = 1 AND remaining_stock <= refill_threshold",
            (user["id"],)
        ).fetchone()["count"]

        today_schedules = conn.execute("""
            SELECT ds.id, dr.status
            FROM dose_schedules ds
            JOIN medicines m ON ds.medicine_id = m.id
            LEFT JOIN dose_records dr ON ds.id = dr.schedule_id AND dr.scheduled_for = ?
            WHERE m.user_id = ? AND m.is_active = 1 AND m.start_date <= ? AND (m.end_date IS NULL OR m.end_date >= ?)
        """, (today_iso, user["id"], today_iso, today_iso)).fetchall()

    today_pending = sum(1 for r in today_schedules if (r["status"] or "unconfirmed") == "unconfirmed")

    reg_ddi = ddi.check_patient_regimen_interactions(user["id"])
    severe_ddi = reg_ddi["severe_count"] if reg_ddi["has_interactions"] else 0

    initial = (display_name[:1] or "U").upper()

    # 1. Clinical Brand Header
    st.sidebar.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; padding: 2px 4px 14px 4px; border-bottom: 1px solid #e2e8f0; margin-bottom: 12px;'>
        <div style='width: 36px; height: 36px; min-width: 36px; border-radius: 10px; background: linear-gradient(135deg, #059669 0%, #0d9488 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: 700; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);'>
            ✚
        </div>
        <div>
            <div style='font-size: 17px; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; line-height: 1.2;'>
                MediAssist <span style='background: #dcfce7; color: #15803d; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 6px; vertical-align: middle;'>AI</span>
            </div>
            <div style='font-size: 11px; color: #64748b; font-weight: 500;'>Clinical Decision Support</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Patient Identity Card
    st.sidebar.markdown(f"""
    <div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 12px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <div style='width: 34px; height: 34px; min-width: 34px; border-radius: 50%; background: #f0fdf4; border: 1.5px solid #10b981; color: #047857; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13.5px;'>
                {initial}
            </div>
            <div style='overflow: hidden; flex: 1;'>
                <div style='font-weight: 700; font-size: 13.5px; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{display_name}</div>
                <div style='font-size: 11px; color: #059669; font-weight: 600; display: flex; align-items: center; gap: 4px;'>
                    <span style='width: 6px; height: 6px; border-radius: 50%; background: #10b981;'></span> {active_meds_count} Prescriptions Active
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Categorized Clinical Navigation
    st.sidebar.markdown("<div style='font-size: 10.5px; font-weight: 700; color: #94a3b8; letter-spacing: 0.6px; margin: 4px 6px 6px 6px; text-transform: uppercase;'>CLINICAL WORKSPACE</div>", unsafe_allow_html=True)

    dose_badge = f"  ({today_pending} Due)" if today_pending > 0 else ""
    ddi_badge = "  🔴 Alert" if severe_ddi > 0 else ""
    stock_badge = "  ⚠️ Refill" if low_stock_count > 0 else ""

    nav_labels = {
        "Home": "🏠  Overview Dashboard",
        "Dose Tracking": f"⏰  Daily Dose Intake{dose_badge}",
        "Medicines": "💊  Prescriptions & Stock",
        "Drug-Drug Interactions": f"🛡️  Safety & Interactions{ddi_badge}",
        "Reminders": f"🔔  Reminders & Refills{stock_badge}",
        "Adherence History": "📊  Compliance Analytics",
        "Adherence Risk Prediction": "🎯  AI Risk Predictor",
        "Food Suggestions": "🥗  Dietary AI & Nutrition",
        "Profile": "👤  Patient Profile",
        "Settings": "⚙️  Settings & Safeguards"
    }

    nav_options = list(nav_labels.keys())

    if st.session_state.nav_page not in nav_options:
        st.session_state.nav_page = "Home"

    selected_nav = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state.nav_page),
        format_func=lambda x: nav_labels.get(x, x),
        label_visibility="collapsed"
    )

    if selected_nav != st.session_state.nav_page:
        st.session_state.nav_page = selected_nav
        st.rerun()

    page = st.session_state.nav_page

    # 4. Persistent AI Status Box & Sign Out
    st.sidebar.markdown("""
    <div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; margin: 18px 0 10px 0;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <span style='font-size: 10.5px; font-weight: 700; color: #475569; letter-spacing: 0.3px;'>AI CLINICAL ENGINE</span>
            <span class='badge-pill badge-green' style='font-size: 9px; padding: 2px 6px;'>v1.2 Active</span>
        </div>
        <div style='font-size: 10.5px; color: #64748b; margin-top: 4px; line-height: 1.3;'>
            Random Forest (AUC 0.90) &bull; ICMR-NIN 500+ &bull; CYP450 DDI
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.nav_page = "Home"
        st.rerun()

    # =====================================
    # HOME PAGE
    # =====================================

    if page == "Home":
        dash_data = get_home_dashboard_data(user["id"])

        # Time-of-day greeting
        from datetime import datetime
        cur_hour = datetime.now().hour
        if cur_hour < 12:
            time_greet = "Good morning"
        elif cur_hour < 17:
            time_greet = "Good afternoon"
        else:
            time_greet = "Good evening"

        today_str = date.today().strftime("%A, %d %B %Y")
        streak_badge = f"<span class='badge-pill badge-amber'>🔥 {dash_data['streak_days']} Day Streak</span>" if dash_data['streak_days'] > 0 else ""

        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 10px;'>
            <div>
                <h1 style='font-size: 26px; margin: 0; color: #0f172a;'>{time_greet}, {display_name} 👋</h1>
                <p style='color: #64748b; margin: 4px 0 0 0; font-size: 13.5px;'>{today_str} &bull; Regimen & Health Overview</p>
            </div>
            <div>
                {streak_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Today's Progress Bar Card
        tot_d = dash_data['today_doses']
        tkn_d = dash_data['today_taken']
        prog_pct = dash_data['today_progress']

        with st.container(border=True):
            p_col1, p_col2 = st.columns([3, 1])
            with p_col1:
                st.markdown(f"**Today's Schedule:** `{tkn_d} of {tot_d} doses confirmed` ({prog_pct:.0f}%)")
                st.progress(prog_pct / 100)
            with p_col2:
                if tot_d == 0:
                    st.caption("No doses scheduled today.")
                elif tkn_d == tot_d:
                    st.markdown("<div style='text-align: right;'><span class='badge-pill badge-green'>✅ All Completed</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: right;'><span class='badge-pill badge-amber'>⏳ {dash_data['today_pending']} Due / Pending</span></div>", unsafe_allow_html=True)

        # Key Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Active Prescriptions", dash_data['active_meds'])
        with m2:
            st.metric("Today's Doses", f"{dash_data['today_taken']} / {dash_data['today_doses']}")
        with m3:
            st.metric("15-Day Adherence", dash_data['adherence_pct'])
        with m4:
            stock_val = f"{dash_data['low_stock_count']} Alert" if dash_data['low_stock_count'] > 0 else "Optimal"
            st.metric("Stock Status", stock_val)

        # Critical Safety Alerts (if any)
        reg_ddi = ddi.check_patient_regimen_interactions(user["id"])
        if reg_ddi["has_interactions"] and reg_ddi["severe_count"] > 0:
            st.error(f"⚠️ **Clinical Medication Safety Alert:** Identified **{reg_ddi['severe_count']} Severe (Contraindicated)** interaction(s) in your active prescriptions.")
            if st.button("Review Full Interaction Report", key="home_btn_ddi"):
                st.session_state.nav_page = "Drug-Drug Interactions"
                st.rerun()

        if dash_data['low_stock_count'] > 0:
            st.warning(f"📦 **Refill Notice:** **{dash_data['low_stock_count']} medicine(s)** are at or below refill threshold.")
            if st.button("Check Stock & Refill Alerts", key="home_btn_stock"):
                st.session_state.nav_page = "Reminders"
                st.rerun()

        # Quick Actions
        st.markdown("#### Quick Actions")
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            with st.container(border=True):
                st.markdown("💊 **Dose Tracking**")
                st.caption("Confirm today's due doses")
                if st.button("Log Doses", key="qa_dose", use_container_width=True):
                    st.session_state.nav_page = "Dose Tracking"
                    st.rerun()
        with q2:
            with st.container(border=True):
                st.markdown("➕ **My Medicines**")
                st.caption("Prescriptions & inventory")
                if st.button("Manage Meds", key="qa_med", use_container_width=True):
                    st.session_state.nav_page = "Medicines"
                    st.rerun()
        with q3:
            with st.container(border=True):
                st.markdown("🛡️ **Safety Check**")
                st.caption("DDI & Disease Clashes")
                if st.button("Safety Scan", key="qa_ddi", use_container_width=True):
                    st.session_state.nav_page = "Drug-Drug Interactions"
                    st.rerun()
        with q4:
            with st.container(border=True):
                st.markdown("🥗 **Dietary AI Chat**")
                st.caption("Meal plans & safety chat")
                if st.button("Consult AI", key="qa_food", use_container_width=True):
                    st.session_state.nav_page = "Food Suggestions"
                    st.rerun()

        # Recent Activity Feed
        st.markdown("#### Recent Medication Events")
        recent_acts = dash_data["recent_activity"]
        if recent_acts:
            for act in recent_acts:
                st_val = act["status"].lower()
                if st_val == "taken":
                    badge_html = "<span class='badge-pill badge-green'>Taken</span>"
                elif st_val == "missed":
                    badge_html = "<span class='badge-pill badge-red'>Missed</span>"
                else:
                    badge_html = "<span class='badge-pill badge-amber'>Unconfirmed</span>"

                st.markdown(
                    f"""
                    <div style='background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <b>{act['medicine_name']}</b> <span style='color: #64748b; font-size: 13px;'>({act['dosage'] or 'Standard dose'})</span>
                            <span style='color: #94a3b8; font-size: 12px; margin-left: 8px;'>Scheduled: {act['scheduled_for']} at {act['dose_time']}</span>
                        </div>
                        <div>
                            {badge_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No recent medication events. Confirm or mark doses under Dose Tracking to view live activity.")

    # =====================================
    # MEDICINES PAGE
    # =====================================

    elif page == "Medicines":

        show_medicines(user["id"])

    # =====================================
    # DRUG-DRUG INTERACTIONS PAGE
    # =====================================

    elif page == "Drug-Drug Interactions":

        show_ddi_checker_page(user["id"])

    # =====================================
    # DOSE TRACKING PAGE
    # =====================================

    elif page == "Dose Tracking":

        show_dose_tracking(user["id"])

    # =====================================
    # REMINDERS PAGE
    # =====================================

    elif page == "Reminders":

        show_reminders(user["id"])

    # =====================================
    # ADHERENCE HISTORY PAGE
    # =====================================

    elif page == "Adherence History":

        show_adherence_history(user["id"])

    # =====================================
    # ADHERENCE RISK PREDICTION PAGE (ML)
    # =====================================

    elif page == "Adherence Risk Prediction":

        show_adherence_risk_page(user["id"])

    # =====================================
    # FOOD SUGGESTIONS PAGE
    # =====================================

    elif page == "Food Suggestions":

        show_food_suggestions_page(user["id"])

    # =====================================
    # PROFILE PAGE
    # =====================================

    elif page == "Profile":

        show_profile(user)

    elif page == "Settings":

        show_settings(user["id"])


# =========================================
# 8. APPLICATION ENTRY POINT
# =========================================

if st.session_state.user is None:

    show_authentication()

else:

    show_dashboard()
