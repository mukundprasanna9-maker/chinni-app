"""User repository for Cadence authentication.

Handles user creation, lookup, and password verification using
bcrypt-style hashing via hashlib (no extra dependency).
"""

import hashlib
import os
from backend.repositories.database import get_connection


def _hash_password(password: str) -> str:
    """Hash a password with a random salt using SHA-256."""
    salt = os.urandom(16).hex()
    pw_hash = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}${pw_hash}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored salt$hash string."""
    if "$" not in stored_hash:
        return False
    salt, pw_hash = stored_hash.split("$", 1)
    check = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return check == pw_hash


def create_user(username: str, password: str, is_admin: bool = False) -> dict | None:
    """Create a new user. Returns the user dict or None if username already exists."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return None

    pw_hash = _hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
        (username, pw_hash, 1 if is_admin else 0),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_user_by_id(user_id)


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, is_admin, created_at FROM users WHERE id = %s",
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_user_by_username(username: str) -> dict | None:
    """Returns the full user row including password_hash for verification."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, password_hash, is_admin, created_at FROM users WHERE username = %s",
        (username,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def authenticate_user(username: str, password: str) -> dict | None:
    """Authenticate a user. Returns user dict (without password_hash) on success, None on failure."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not _verify_password(password, user["password_hash"]):
        return None
    # Return user info without the password hash
    return {
        "id": user["id"],
        "username": user["username"],
        "is_admin": bool(user["is_admin"]),
        "created_at": user.get("created_at"),
    }


def get_all_users() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, is_admin, created_at FROM users ORDER BY id ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def ensure_admin_exists(username: str = "admin", password: str = "admin123") -> None:
    """Ensure a default admin account exists. Called during DB init."""
    user = get_user_by_username(username)
    if not user:
        create_user(username, password, is_admin=True)
        print(f"[Auth] Default admin account created (username: {username}, password: {password})")
    else:
        print(f"[Auth] Admin account '{username}' already exists.")


def update_user_credentials(
    user_id: int,
    current_password: str,
    new_username: str | None = None,
    new_password: str | None = None,
) -> tuple[dict | None, str | None]:
    """Verify current_password, then update username and/or password.

    Returns (updated_user_dict, None) on success or (None, error_code) on failure.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, password_hash, is_admin, created_at FROM users WHERE id = %s",
        (user_id,),
    )
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return None, "NOT_FOUND"

    if not _verify_password(current_password, user["password_hash"]):
        cursor.close()
        conn.close()
        return None, "INVALID_PASSWORD"

    old_username = user["username"]
    final_username = new_username.strip() if new_username and new_username.strip() else old_username
    final_hash = _hash_password(new_password) if new_password else user["password_hash"]

    if final_username != old_username:
        cursor.execute(
            "SELECT id FROM users WHERE username = %s AND id != %s",
            (final_username, user_id),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "USERNAME_TAKEN"

    cursor.execute(
        "UPDATE users SET username = %s, password_hash = %s WHERE id = %s",
        (final_username, final_hash, user_id),
    )
    # Keep student profile name synced if it matched the old username
    if final_username != old_username:
        cursor.execute(
            "UPDATE students SET name = %s WHERE user_id = %s AND name = %s",
            (final_username, user_id, old_username),
        )
    conn.commit()
    cursor.close()
    conn.close()

    updated = get_user_by_id(user_id)
    if updated:
        updated["is_admin"] = bool(updated["is_admin"])
    return updated, None
