
import hashlib
import secrets
import sqlite3

from database import get_connection


# Password security settings
HASH_NAME = "sha256"
ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password, salt=None):
    """Hash a password securely using PBKDF2."""

    if salt is None:
        salt = secrets.token_hex(SALT_BYTES)

    password_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        bytes.fromhex(salt),
        ITERATIONS
    ).hex()

    return password_hash, salt


def create_user(username, password):
    """Register a new user."""

    username = username.strip().lower()

    if len(username) < 3:
        return False, "Username must contain at least 3 characters.", None

    if len(password) < 8:
        return False, "Password must contain at least 8 characters.", None

    password_hash, salt = hash_password(password)

    try:
        with get_connection() as conn:

            cursor = conn.execute(
                """
                INSERT INTO users (username, password_hash, password_salt)
                VALUES (?, ?, ?)
                """,
                (username, password_hash, salt)
            )

            user_id = cursor.lastrowid

            # Create the user's default profile
            conn.execute(
                """
                INSERT INTO user_profiles (user_id)
                VALUES (?)
                """,
                (user_id,)
            )

            # Create default intervention preferences
            conn.execute(
                """
                INSERT INTO intervention_preferences (user_id)
                VALUES (?)
                """,
                (user_id,)
            )

        return True, "Account created successfully!", user_id

    except sqlite3.IntegrityError:
        return False, "This username is already registered.", None

    except sqlite3.Error:
        return False, "A database error occurred. Please try again.", None


def verify_user(username, password):
    """Verify login credentials."""

    username = username.strip().lower()

    try:
        with get_connection() as conn:
            user = conn.execute(
                """
                SELECT id, username, password_hash, password_salt
                FROM users
                WHERE username = ?
                """,
                (username,)
            ).fetchone()

        if user is None:
            return None

        stored_hash = user["password_hash"]
        salt = user["password_salt"]

        entered_hash, _ = hash_password(password, salt)

        if secrets.compare_digest(entered_hash, stored_hash):
            return {
                "id": user["id"],
                "username": user["username"]
            }

        return None

    except sqlite3.Error:
        return None
