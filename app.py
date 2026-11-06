
import streamlit as st

from auth import create_user, verify_user
from database import get_connection

from medicines import show_medicines
from dose_tracking import show_dose_tracking
from reminders import show_reminders
from adherence_history import show_adherence_history


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
# 4. PROFILE DATABASE FUNCTIONS
# =========================================

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
# 7. MAIN DASHBOARD
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

        st.subheader("Your Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Active Medicines", "—")

        with col2:
            st.metric("Today's Doses", "—")

        with col3:
            st.metric("Adherence Status", "—")

        st.divider()

        st.subheader("Quick Access")

        col1, col2 = st.columns(2)

        with col1:

            with st.container(border=True):

                st.subheader("💊 Medicine Management")

                st.write(
                    "Manage regular and temporary medicines, "
                    "medication schedules, and stock."
                )

                st.caption(
                    "Use the Medicines page to manage your medicines."
                )

        with col2:

            with st.container(border=True):

                st.subheader("🥗 Food Suggestions")

                st.write(
                    "Explore food suggestions based on your "
                    "preferences and dietary restrictions."
                )

                st.caption(
                    "Food recommendation integration pending."
                )

        st.divider()

        st.subheader("Medication Activity")

        st.info(
            "Your recent medication activity and dose updates "
            "will appear here once the dashboard summary is connected."
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
    # FOOD SUGGESTIONS PAGE
    # =====================================

    elif page == "Food Suggestions":

        st.title("🥗 Food Suggestions")

        st.write(
            "Explore food suggestions based on your dietary "
            "preferences and restrictions."
        )

        st.info(
            "The food recommendation module will be integrated here."
        )

    # =====================================
    # PROFILE PAGE
    # =====================================

    elif page == "Profile":

        show_profile(user)

    # =====================================
    # SETTINGS PAGE
    # =====================================

    elif page == "Settings":

        st.title("⚙️ Settings")

        st.write("Manage your application preferences.")

        st.info(
            "Notification preferences and optional caregiver "
            "settings will be connected here."
        )


# =========================================
# 8. APPLICATION ENTRY POINT
# =========================================

if st.session_state.user is None:

    show_authentication()

else:

    show_dashboard()
