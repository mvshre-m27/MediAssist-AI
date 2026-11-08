
import sqlite3
from pathlib import Path
from contextlib import contextmanager


# ==================================================
# 1. DATABASE LOCATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "mediassist.db"


# ==================================================
# 2. DATABASE CONNECTION
# ==================================================

@contextmanager
def get_connection():
    """Create and safely close a SQLite database connection."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==================================================
# 3. INITIALIZE DATABASE AND CREATE TABLES
# ==================================================

def init_db():

    with get_connection() as conn:

        # ------------------------------------------
        # TABLE 1: USERS
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ------------------------------------------
        # TABLE 2: USER PROFILES
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                full_name TEXT,
                age INTEGER,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 3: MEDICINES
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,

                medicine_type TEXT NOT NULL
                    CHECK (medicine_type IN ('regular', 'temporary')),

                dosage TEXT,
                instructions TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT,

                total_stock REAL DEFAULT 0,
                remaining_stock REAL DEFAULT 0,
                refill_threshold REAL DEFAULT 0,

                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 4: DOSE SCHEDULES
        # One row represents one dose timing.
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS dose_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                dose_time TEXT NOT NULL,

                FOREIGN KEY (medicine_id)
                    REFERENCES medicines(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 5: DOSE RECORDS
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS dose_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                scheduled_for TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'unconfirmed'
                    CHECK (
                        status IN ('taken', 'missed', 'unconfirmed')
                    ),

                taken_at TIMESTAMP,

                UNIQUE (schedule_id, scheduled_for),

                FOREIGN KEY (schedule_id)
                    REFERENCES dose_schedules(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 6: FOOD PREFERENCES
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS food_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,

                diet_type TEXT,
                allergies TEXT,
                dietary_restrictions TEXT,
                food_preferences TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 7: INTERVENTION PREFERENCES
        # User controls supportive reminders.
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS intervention_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,

                gentle_reminders_enabled INTEGER NOT NULL DEFAULT 0
                    CHECK (gentle_reminders_enabled IN (0, 1)),

                caregiver_alerts_enabled INTEGER NOT NULL DEFAULT 0
                    CHECK (caregiver_alerts_enabled IN (0, 1)),

                alert_threshold TEXT NOT NULL DEFAULT 'high'
                    CHECK (alert_threshold IN ('medium', 'high')),

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 8: CAREGIVER CONTACTS
        # Consent must be recorded before alerts.
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS caregiver_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,

                caregiver_name TEXT NOT NULL,
                relationship TEXT,
                contact_method TEXT NOT NULL
                    CHECK (contact_method IN ('email', 'phone')),

                contact_value TEXT NOT NULL,

                consent_given INTEGER NOT NULL DEFAULT 0
                    CHECK (consent_given IN (0, 1)),

                consent_at TIMESTAMP,
                is_enabled INTEGER NOT NULL DEFAULT 0
                    CHECK (is_enabled IN (0, 1)),

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 9: ADHERENCE ASSESSMENTS
        # Stores ML model predictions.
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS adherence_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,

                risk_level TEXT NOT NULL
                    CHECK (risk_level IN ('low', 'medium', 'high')),

                risk_score REAL,
                model_version TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # TABLE 10: INTERVENTION LOGS
        # Stores supportive reminders and alerts.
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS intervention_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,
                assessment_id INTEGER,

                caregiver_contact_id INTEGER,

                intervention_type TEXT NOT NULL
                    CHECK (
                        intervention_type IN (
                            'gentle_reminder',
                            'caregiver_alert'
                        )
                    ),

                delivery_status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (
                        delivery_status IN (
                            'pending',
                            'sent',
                            'failed'
                        )
                    ),

                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE,

                FOREIGN KEY (assessment_id)
                    REFERENCES adherence_assessments(id)
                    ON DELETE SET NULL,

                FOREIGN KEY (caregiver_contact_id)
                    REFERENCES caregiver_contacts(id)
                    ON DELETE SET NULL
            )
        """)

        # ------------------------------------------
        # TABLE 11: USER COMORBIDITIES
        # Stores diagnosed chronic medical conditions
        # ------------------------------------------

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_comorbidities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                condition_key TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, condition_key),
                FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ------------------------------------------
        # INDEXES FOR FASTER DATA RETRIEVAL
        # ------------------------------------------

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_medicines_user
            ON medicines(user_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedules_medicine
            ON dose_schedules(medicine_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_records_schedule
            ON dose_records(schedule_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessments_user
            ON adherence_assessments(user_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interventions_user
            ON intervention_logs(user_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_comorbidities_user
            ON user_comorbidities(user_id)
        """)

    print("MediAssist database initialized successfully!")


# ==================================================
# 4. COMORBIDITY MANAGEMENT FUNCTIONS
# ==================================================

KNOWN_COMORBIDITY_LABELS = {
    "diabetes": "Type 2 Diabetes Mellitus",
    "hypertension": "Essential Hypertension",
    "ckd": "Chronic Kidney Disease (CKD / Renal Impairment)",
    "heart_disease": "Coronary Artery Disease / Heart Failure",
    "dyslipidemia": "Dyslipidemia & High Cholesterol",
    "gout": "Hyperuricemia & Gout",
    "gerd": "Acid Reflux / GERD / Gastric Ulcer",
    "asthma": "Bronchial Asthma / COPD",
    "liver_disease": "Fatty Liver (NAFLD) / Hepatic Impairment",
    "osteoporosis": "Osteopenia / Osteoporosis"
}


def get_user_comorbidities(user_id):
    """Fetch diagnosed comorbidity records for a user."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT condition_key, condition_name
            FROM user_comorbidities
            WHERE user_id = ?
            ORDER BY condition_name ASC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


def save_user_comorbidities(user_id, condition_keys):
    """Save selected chronic comorbidities for a user."""
    with get_connection() as conn:
        conn.execute("DELETE FROM user_comorbidities WHERE user_id = ?", (user_id,))
        for key in condition_keys:
            if not key or not str(key).strip():
                continue
            k = str(key).strip().lower()
            name = KNOWN_COMORBIDITY_LABELS.get(k, k.replace("_", " ").title())
            conn.execute("""
                INSERT OR IGNORE INTO user_comorbidities (user_id, condition_key, condition_name)
                VALUES (?, ?, ?)
            """, (user_id, k, name))


# ==================================================
# 5. GET ALL TABLE NAMES
# ==================================================

def get_table_names():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

    return [row["name"] for row in rows]


# ==================================================
# 5. INITIALIZE DATABASE
# ==================================================

init_db()
