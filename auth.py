
import hashlib
import re
import secrets
import sqlite3

import streamlit as st

DB_FILE = "ecoscan.db"
ITERATIONS = 600_000


def get_connection():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    return password_hash.hex(), salt.hex()


def verify_password(password, saved_hash, saved_salt):
    try:
        salt = bytes.fromhex(saved_salt)
        calculated_hash, _ = hash_password(password, salt)

        return secrets.compare_digest(
            calculated_hash,
            saved_hash
        )
    except (ValueError, TypeError):
        return False


def register_user(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name or len(name) > 60:
        return False, "Enter a name between 1 and 60 characters."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if len(password) > 128:
        return False, "Password must not exceed 128 characters."

    password_hash, salt = hash_password(password)

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (name, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, password_hash, salt)
            )

        return True, "Account created successfully! You can now log in."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def authenticate_user(email, password):
    email = email.strip().lower()

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT id, name, email, password_hash, salt
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if user is None:
        return None

    if not verify_password(
        password,
        user["password_hash"],
        user["salt"]
    ):
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }


def show_auth():
    init_db()

    st.title("🌿 Welcome to EcoScan")
    st.write("Sign in or create an account to explore EcoScan.")

    tab = st.radio(
        "Account access",
        ["Login", "Register"],
        horizontal=True,
        key="auth_tab"
    )

    if tab == "Register":
        with st.form("registration_form"):
            name = st.text_input(
                "Full name",
                max_chars=60
            )
            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password",
                max_chars=128
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                max_chars=128
            )

            submitted = st.form_submit_button(
                "Create Account 🌱",
                use_container_width=True
            )

        if submitted:
            if password != confirm_password:
                st.error("The passwords do not match.")
            else:
                success, message = register_user(
                    name, email, password
                )

                if success:
                    st.success(message)
                    st.info("Select Login above to sign in.")
                else:
                    st.error(message)

    else:
        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login 🌿",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if not email.strip() or not password:
                st.error("Enter your email and password.")
            else:
                user = authenticate_user(email, password)

                if user:
                    st.session_state["current_user"] = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    st.caption(
        "Your password is stored as a salted hash, not as plain text."
    )
