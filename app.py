
import streamlit as st
from datetime import date

from auth import create_user, verify_user
from database import get_connection

from medicines import show_medicines
from dose_tracking import show_dose_tracking
from reminders import show_reminders
from adherence_history import show_adherence_history, get_adherence_data, calculate_adherence
from adherence_risk import show_adherence_risk_page
from food_suggestions import show_food_suggestions_page


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
# 3. CUSTOM DESIGN
# =========================================

st.markdown("""
<style>

.stApp {
    background-color: #f4faf7;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    color: #145c49;
    font-size: 40px;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    color: #648176;
    margin-bottom: 30px;
}

.dashboard-heading {
    color: #145c49;
    font-weight: 700;
}

div.stButton > button {
    border-radius: 10px;
    width: 100%;
    min-height: 42px;
}

[data-testid="stSidebar"] {
    background-color: #e9f5ef;
}

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #dcebe3;
    padding: 18px;
    border-radius: 12px;
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

        today_doses = conn.execute("""
            SELECT COUNT(ds.id) as count
            FROM dose_schedules ds
            JOIN medicines m ON ds.medicine_id = m.id
            WHERE m.user_id = ?
              AND m.is_active = 1
              AND m.start_date <= ?
              AND (m.end_date IS NULL OR m.end_date >= ?)
        """, (user_id, today, today)).fetchone()["count"]

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

    records = get_adherence_data(user_id, days=7)
    adherence_pct = "No history"
    if records:
        total, taken, missed, unconfirmed, adherence = calculate_adherence(records)
        if (taken + missed) > 0:
            adherence_pct = f"{adherence:.1f}%"
        else:
            adherence_pct = "Unconfirmed"

    return {
        "active_meds": active_meds,
        "today_doses": today_doses,
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

    st.markdown(
        '<div class="main-title">💚 MediAssist</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Your health, our priority</div>',
        unsafe_allow_html=True
    )

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # -------------------------------------
    # LOGIN
    # -------------------------------------

    with login_tab:

        st.subheader("Welcome back!")

        with st.form("login_form"):

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if submitted:

                if not username.strip() or not password:

                    st.error(
                        "Please enter both username and password."
                    )

                else:

                    user = verify_user(username, password)

                    if user:

                        st.session_state.user = user

                        st.success("Login successful!")

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

    # -------------------------------------
    # REGISTRATION
    # -------------------------------------

    with register_tab:

        st.subheader("Create your MediAssist account")

        with st.form("register_form"):

            new_username = st.text_input(
                "Choose a username"
            )

            new_password = st.text_input(
                "Create password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            registered = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

            if registered:

                if not new_username.strip():

                    st.error("Please enter a username.")

                elif not new_password:

                    st.error("Please enter a password.")

                elif new_password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    success, message, user_id = create_user(
                        new_username,
                        new_password
                    )

                    if success:

                        st.success(message)

                        st.info(
                            "You can now log in using your new account."
                        )

                    else:

                        st.error(message)


# =========================================
# 6. USER PROFILE PAGE
# =========================================

def show_profile(user):

    st.title("👤 My Profile")

    st.write(
        "Manage your personal information and food preferences."
    )

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

                    st.success(
                        "Your profile has been saved successfully!"
                    )

                except Exception as e:

                    st.error(f"Unable to save profile: {e}")

    except Exception as e:

        st.error(f"Unable to load profile: {e}")


# =========================================
# 7. SETTINGS PAGE
# =========================================

def show_settings(user_id):
    st.title("⚙️ Application Settings")
    st.write("Manage your notification preferences, intervention safeguards, and caregiver contacts.")

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
    # SIDEBAR
    # -------------------------------------

    st.sidebar.title("💚 MediAssist")

    st.sidebar.caption("Your health, our priority")

    st.sidebar.divider()

    st.sidebar.write(
        f"Welcome, **{user['username']}**"
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Medicines",
            "Dose Tracking",
            "Reminders",
            "Adherence History",
            "Adherence Risk Prediction",
            "Food Suggestions",
            "Profile",
            "Settings"
        ]
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.user = None

        st.rerun()

    # =====================================
    # HOME PAGE
    # =====================================

    if page == "Home":

        st.markdown(
            '<h1 class="dashboard-heading">'
            'Welcome to MediAssist 💚'
            '</h1>',
            unsafe_allow_html=True
        )

        st.write(
            "Your personal medication management "
            "and health support dashboard."
        )

        st.divider()

        dash_data = get_home_dashboard_data(user["id"])

        st.subheader("Your Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Active Medicines", f"{dash_data['active_meds']}")

        with col2:
            st.metric("Today's Doses", f"{dash_data['today_doses']}")

        with col3:
            st.metric("7-Day Adherence Status", f"{dash_data['adherence_pct']}")

        st.divider()

        st.subheader("Quick Access")

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.subheader("💊 Medicines")
                st.write(
                    "Manage regular and temporary medicines, "
                    "schedules, and remaining stock."
                )
                st.caption("Track & configure daily dose times.")

        with col2:
            with st.container(border=True):
                st.subheader("🎯 Risk Prediction")
                st.write(
                    "Run our trained Machine Learning pipeline to "
                    "assess medication non-adherence risk."
                )
                st.caption("Powered by Random Forest (ROC-AUC: 0.90).")

        with col3:
            with st.container(border=True):
                st.subheader("🥗 Food Suggestions")
                st.write(
                    "Explore clinical food recommendations based on "
                    "your dietary preferences and health needs."
                )
                st.caption("DASH & Low-GI aligned nutrition.")

        st.divider()

        st.subheader("Recent Medication Activity")

        recent_acts = dash_data["recent_activity"]
        if recent_acts:
            for act in recent_acts:
                status_color = "#2e7d32" if act["status"] == "taken" else ("#d32f2f" if act["status"] == "missed" else "#ed6c02")
                st.markdown(
                    f"""
                    <div style='background: white; border: 1px solid #dcebe3; border-radius: 8px; padding: 10px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <b>{act['medicine_name']}</b> ({act['dosage'] or 'No dosage specified'}) &nbsp;|&nbsp;
                            <span style='color: #666;'>Scheduled: {act['scheduled_for']} at {act['dose_time']}</span>
                        </div>
                        <span style='background-color: {status_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; text-transform: uppercase; font-weight: bold;'>
                            {act['status']}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info(
                "No recent medication activity recorded yet. "
                "Confirm or mark doses under **Dose Tracking** to see real-time updates here."
            )

    # =====================================
    # MEDICINES PAGE
    # =====================================

    elif page == "Medicines":

        show_medicines(user["id"])

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
