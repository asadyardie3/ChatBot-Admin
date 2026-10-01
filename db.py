import os
import re
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com").lower()
EMAIL_OK = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
FIELDS = {"phone", "city", "name", "email"}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                phone TEXT,
                city TEXT
            )"""
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (email, name) VALUES (?, ?)",
            (ADMIN_EMAIL, "Admin"),
        )


def name_from_email(email):
    local = email.split("@")[0]
    return " ".join(re.split(r"[._\-+]+", local)).title()


def find_by_email(email):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE lower(email)=?", (email.strip().lower(),)
        ).fetchone()


def resolve_user(who):
    who = who.strip().strip("\"'").lower()
    who = re.sub(r"['’]s$", "", who)
    candidates = [who]
    if who.endswith("s") and "@" not in who:
        candidates.append(who[:-1])
    with get_conn() as conn:
        for c in candidates:
            rows = conn.execute(
                """SELECT * FROM users
                   WHERE lower(email)=? OR lower(name)=?
                      OR lower(email) LIKE ? OR lower(name) LIKE ?""",
                (c, c, c + "@%", c + " %"),
            ).fetchall()
            if rows:
                return rows
    return []


def _ambiguous(rows):
    emails = ", ".join(r["email"] for r in rows)
    return f"More than one user matches: {emails}. Please use the full email."


def add_user(email, phone=None):
    email = email.strip().lower()
    if not EMAIL_OK.match(email):
        return f"'{email}' is not a valid email address."
    with get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone()
        if exists:
            return f"User {email} already exists."
        conn.execute(
            "INSERT INTO users (email, name, phone) VALUES (?, ?, ?)",
            (email, name_from_email(email), phone),
        )
    return f"Done. Added {email}" + (f" with phone {phone}." if phone else ".")


def delete_user(who, current_email):
    rows = resolve_user(who)
    if not rows:
        return f"I couldn't find a user matching '{who}'."
    if len(rows) > 1:
        return _ambiguous(rows)
    row = rows[0]
    if row["email"].lower() == current_email.lower():
        return "You can't remove your own account while logged in."
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (row["id"],))
    return f"Done. Removed {row['email']}."


def update_user(who, field, value, current_email):
    if field not in FIELDS:
        return "I can update phone, city, name or email."
    rows = resolve_user(who)
    if not rows:
        return f"I couldn't find a user matching '{who}'."
    if len(rows) > 1:
        return _ambiguous(rows)
    row = rows[0]
    if field == "email":
        value = value.strip().lower()
        if not EMAIL_OK.match(value):
            return f"'{value}' is not a valid email address."
        if row["email"].lower() == current_email.lower():
            return "You can't change your own login email."
        with get_conn() as conn:
            taken = conn.execute(
                "SELECT 1 FROM users WHERE email=? AND id<>?", (value, row["id"])
            ).fetchone()
        if taken:
            return f"{value} is already used by another user."
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {field}=? WHERE id=?", (value, row["id"]))
    return f"Done. Updated {row['email']}: {field} is now {value}."


def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    if not rows:
        return "No users yet."
    lines = [
        f"{r['email']} | name: {r['name'] or '-'} | phone: {r['phone'] or '-'} | city: {r['city'] or '-'}"
        for r in rows
    ]
    return "Users:\n" + "\n".join(lines)