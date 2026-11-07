"""
MediAssist-AI: Demo Account & Sample Data Seeder
Creates a clean demonstration profile with realistic chronic care data:
- User: 'demo_patient' / 'Demo@12345'
- Profile: Age 58, Hypertension & Diabetes
- Food Preferences: Vegetarian, Low-Sugar & Low-Sodium restrictions, Peanut Allergy
- Active Medicines: Metformin (500mg), Amlodipine (5mg), Atorvastatin (10mg)
- Dose History: 15 days of logged dose records (~83% adherence rate)
- Caregiver: Sunita Sharma (Spouse)
"""

from datetime import date, datetime, timedelta
import random
from database import get_connection, init_db
from auth import create_user, verify_user

DEMO_USERNAME = "demo_patient"
DEMO_PASSWORD = "Demo@12345"

def seed_demo():
    print("=" * 60)
    print("MediAssist-AI: Seeding Realistic Demonstration Data")
    print("=" * 60)
    
    init_db()

    # 1. Create or retrieve demo user
    user = verify_user(DEMO_USERNAME, DEMO_PASSWORD)
    if not user:
        success, msg, user_id = create_user(DEMO_USERNAME, DEMO_PASSWORD)
        if not success:
            print(f"Error creating user: {msg}")
            return
        user = verify_user(DEMO_USERNAME, DEMO_PASSWORD)
        print(f"Created demo user: '{DEMO_USERNAME}' (ID: {user['id']})")
    else:
        print(f"Demo user '{DEMO_USERNAME}' already exists (ID: {user['id']})")

    user_id = user["id"]

    with get_connection() as conn:
        # 2. Update Profile & Food Preferences
        conn.execute("""
            UPDATE user_profiles
            SET full_name = 'Ramesh Sharma', age = 58
            WHERE user_id = ?
        """, (user_id,))

        conn.execute("""
            INSERT INTO food_preferences (user_id, diet_type, allergies, dietary_restrictions, food_preferences)
            VALUES (?, 'Vegetarian', 'Peanuts', 'Low-sugar, Low-sodium (DASH)', 'Prefers oats, green vegetables, moong dal; avoids fried snacks')
            ON CONFLICT(user_id) DO UPDATE SET
                diet_type = excluded.diet_type,
                allergies = excluded.allergies,
                dietary_restrictions = excluded.dietary_restrictions,
                food_preferences = excluded.food_preferences
        """, (user_id,))

        # 3. Update Intervention Preferences
        conn.execute("""
            INSERT INTO intervention_preferences (user_id, gentle_reminders_enabled, caregiver_alerts_enabled, alert_threshold)
            VALUES (?, 1, 1, 'high')
            ON CONFLICT(user_id) DO UPDATE SET
                gentle_reminders_enabled = 1,
                caregiver_alerts_enabled = 1,
                alert_threshold = 'high'
        """, (user_id,))

        # 4. Caregiver Contact
        existing_cg = conn.execute("SELECT id FROM caregiver_contacts WHERE user_id = ?", (user_id,)).fetchone()
        if not existing_cg:
            conn.execute("""
                INSERT INTO caregiver_contacts (user_id, caregiver_name, relationship, contact_method, contact_value, consent_given, is_enabled)
                VALUES (?, 'Sunita Sharma', 'Spouse', 'phone', '+91 98765 43210', 1, 1)
            """, (user_id,))

        # 5. Clear old medicines and schedules for fresh seed
        conn.execute("DELETE FROM medicines WHERE user_id = ?", (user_id,))

        # 6. Add Medicines
        today = date.today()
        start_date = (today - timedelta(days=30)).isoformat()

        # Med 1: Metformin (Twice daily, normal stock)
        cur1 = conn.execute("""
            INSERT INTO medicines (user_id, medicine_name, medicine_type, dosage, instructions, start_date, total_stock, remaining_stock, refill_threshold, is_active)
            VALUES (?, 'Metformin HCl', 'regular', '500 mg', 'Take with meals (breakfast & dinner)', ?, 60, 42, 10, 1)
        """, (user_id, start_date))
        m1_id = cur1.lastrowid
        cur_ds1 = conn.execute("INSERT INTO dose_schedules (medicine_id, dose_time) VALUES (?, '08:30')", (m1_id,))
        s1_id = cur_ds1.lastrowid
        cur_ds2 = conn.execute("INSERT INTO dose_schedules (medicine_id, dose_time) VALUES (?, '20:30')", (m1_id,))
        s2_id = cur_ds2.lastrowid

        # Med 2: Amlodipine (Once daily in morning, normal stock)
        cur2 = conn.execute("""
            INSERT INTO medicines (user_id, medicine_name, medicine_type, dosage, instructions, start_date, total_stock, remaining_stock, refill_threshold, is_active)
            VALUES (?, 'Amlodipine Besylate', 'regular', '5 mg', 'Take once daily in morning for blood pressure', ?, 30, 18, 7, 1)
        """, (user_id, start_date))
        m2_id = cur2.lastrowid
        cur_ds3 = conn.execute("INSERT INTO dose_schedules (medicine_id, dose_time) VALUES (?, '09:00')", (m2_id,))
        s3_id = cur_ds3.lastrowid

        # Med 3: Atorvastatin (Low stock alert test: remaining 4 <= threshold 7)
        cur3 = conn.execute("""
            INSERT INTO medicines (user_id, medicine_name, medicine_type, dosage, instructions, start_date, total_stock, remaining_stock, refill_threshold, is_active)
            VALUES (?, 'Atorvastatin Calcium', 'regular', '10 mg', 'Take at bedtime for cholesterol management', ?, 30, 4, 7, 1)
        """, (user_id, start_date))
        m3_id = cur3.lastrowid
        cur_ds4 = conn.execute("INSERT INTO dose_schedules (medicine_id, dose_time) VALUES (?, '21:30')", (m3_id,))
        s4_id = cur_ds4.lastrowid

        # 7. Seed Past 15 Days of Dose Records (~83% adherence rate)
        schedules = [s1_id, s2_id, s3_id, s4_id]
        random.seed(42) # Deterministic for consistent demonstrations

        for d in range(15, 0, -1):
            past_day = (today - timedelta(days=d)).isoformat()
            for sched in schedules:
                # 85% probability taken, 15% missed
                outcome = "taken" if random.random() < 0.85 else "missed"
                taken_timestamp = f"{past_day} 09:15:00" if outcome == "taken" else None
                conn.execute("""
                    INSERT INTO dose_records (schedule_id, scheduled_for, status, taken_at)
                    VALUES (?, ?, ?, ?)
                """, (sched, past_day, outcome, taken_timestamp))

        # 8. Seed Today's Doses (Some taken, some due)
        conn.execute("""
            INSERT INTO dose_records (schedule_id, scheduled_for, status, taken_at)
            VALUES (?, ?, 'taken', ?)
        """, (s1_id, today.isoformat(), f"{today.isoformat()} 08:35:00"))

        conn.execute("""
            INSERT INTO dose_records (schedule_id, scheduled_for, status, taken_at)
            VALUES (?, ?, 'taken', ?)
        """, (s3_id, today.isoformat(), f"{today.isoformat()} 09:05:00"))

        # s2_id and s4_id left unconfirmed for tonight's doses!

    print("Successfully seeded demo data:")
    print("  User       : demo_patient")
    print("  Password   : Demo@12345")
    print("  Medicines  : 3 active (Metformin, Amlodipine, Atorvastatin [Low Stock Alert])")
    print("  Doses      : 15-day historical timeline populated (~85% adherence)")
    print("  Profile    : Ramesh Sharma (Age 58, Vegetarian, Peanuts excluded, Low-sugar/Low-sodium)")
    print("=" * 60)

if __name__ == '__main__':
    seed_demo()
