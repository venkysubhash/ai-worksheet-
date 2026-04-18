# ==========================================================
# CAIGS ULTRA AI - DATABASE MODULE (COMPLETE)
# ==========================================================

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

DB_NAME = "learning.db"


# ==========================================================
# CONNECTION MANAGER
# ==========================================================

@contextmanager
def get_connection():

    conn = None

    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA journal_mode=WAL;")

        yield conn

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

def init_db():

    if not os.path.exists(DB_NAME):
        open(DB_NAME, "w").close()

    with get_connection() as conn:

        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            file_name TEXT,
            download_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            chapter TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ADD THIS TABLE
        conn.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            attempt_time DATETIME
        )
        """)

# ==========================================================
# AUTO ADMIN CREATION
# ==========================================================

def ensure_default_admin(hash_password_func):

    with get_connection() as conn:

        cur = conn.execute("SELECT COUNT(*) as total FROM users")
        row = cur.fetchone()

        if row["total"] == 0:

            hashed = hash_password_func("subhash123")

            conn.execute(
                """
                INSERT INTO users (username,password,role)
                VALUES (?,?,?)
                """,
                ("subhash", hashed, "admin")
            )
# ==========================================================
# USER MANAGEMENT
# ==========================================================

def create_user(school_name, username, email, password):

    with get_connection() as conn:

        conn.execute("""
        INSERT INTO users (school_name, username, email, password)
        VALUES (?, ?, ?, ?)
        """, (school_name, username, email, password))


def get_user(username):

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT * FROM users
        WHERE username = ?
        """, (username,))

        return cur.fetchone()


def get_all_users():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT id, username, role, created_at
        FROM users
        ORDER BY username
        """)

        return cur.fetchall()


def delete_user(username):

    with get_connection() as conn:

        conn.execute("""
        DELETE FROM users
        WHERE username = ?
        """, (username,))


# ==========================================================
# DOWNLOAD TRACKING
# ==========================================================

def log_download(username, file_name):

    with get_connection() as conn:

        conn.execute("""
        INSERT INTO downloads (username,file_name)
        VALUES (?,?)
        """, (username, file_name))


def get_user_downloads(username):

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT file_name, download_time
        FROM downloads
        WHERE username = ?
        ORDER BY download_time DESC
        """, (username,))

        return cur.fetchall()


def get_all_downloads():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT file_name, download_time as timestamp
        FROM downloads
        WHERE username = ?
        ORDER BY download_time DESC
        """, (username,))

        return cur.fetchall()


# ==========================================================
# PERFORMANCE RESULTS
# ==========================================================

def save_result(student_name, chapter, score, total):

    if not student_name or not chapter:
        return False

    if total <= 0:
        return False

    try:
        score = int(score)
        total = int(total)
    except:
        return False

    percentage = round((score / total) * 100, 2)

    with get_connection() as conn:

        conn.execute("""
        INSERT INTO performance
        (student_name, chapter, score, total, percentage, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_name.strip(),
            chapter.strip(),
            score,
            total,
            percentage,
            datetime.now()
        ))

    return True


# ==========================================================
# STUDENT STATS
# ==========================================================

def get_student_stats(student_name):

    if not student_name:
        return []

    with get_connection() as conn:

        cursor = conn.execute("""
        SELECT chapter, score, total, percentage, timestamp
        FROM performance
        WHERE student_name = ?
        ORDER BY timestamp DESC
        """, (student_name.strip(),))

        rows = cursor.fetchall()

        return [
            (
                row["chapter"],
                row["score"],
                row["total"],
                row["percentage"],
                row["timestamp"]
            )
            for row in rows
        ]


# ==========================================================
# STUDENT LIST
# ==========================================================

def get_all_students():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT DISTINCT student_name
        FROM performance
        ORDER BY student_name
        """)

        rows = cur.fetchall()

        return [row["student_name"] for row in rows]


# ==========================================================
# DELETE STUDENT DATA
# ==========================================================

def delete_student_records(student_name):

    with get_connection() as conn:

        conn.execute("""
        DELETE FROM performance
        WHERE student_name = ?
        """, (student_name,))

    return True
# ==========================================================
# 🧠 STUDENT INTELLIGENCE ENGINE (PATENT CORE)
# ==========================================================

def get_student_level(student_name):

    if not student_name:
        return "medium"

    stats = get_student_stats(student_name)

    if not stats:
        return "medium"

    try:
        percentages = [row[3] for row in stats if row[3] is not None]

        if not percentages:
            return "medium"

        avg = sum(percentages) / len(percentages)

        if avg < 40:
            return "easy"
        elif avg < 70:
            return "medium"
        else:
            return "hard"

    except Exception:
        return "medium"


# ----------------------------------------------------------
# 📊 PERFORMANCE TREND ANALYSIS
# ----------------------------------------------------------

def get_student_trend(student_name):

    stats = get_student_stats(student_name)

    if len(stats) < 2:
        return "stable"

    percentages = [row[3] for row in stats if row[3] is not None]

    if len(percentages) < 2:
        return "stable"

    # compare last vs first
    if percentages[0] > percentages[-1]:
        return "improving"
    elif percentages[0] < percentages[-1]:
        return "declining"
    else:
        return "stable"


# ----------------------------------------------------------
# 🎯 RECOMMENDED DIFFICULTY (SMART ADAPTATION)
# ----------------------------------------------------------

def get_adaptive_difficulty(student_name):

    level = get_student_level(student_name)
    trend = get_student_trend(student_name)

    # 🔴 PATENT LOGIC: dynamic adjustment

    if trend == "improving" and level == "medium":
        return "hard"

    if trend == "declining" and level == "medium":
        return "easy"

    return level

# ==========================================================
# CLEAR DATABASE
# ==========================================================

def clear_database():

    with get_connection() as conn:
        conn.execute("DELETE FROM performance")

    return True

# ==========================================================
# LOGIN ATTEMPT TRACKING (RATE LIMIT SUPPORT)
# ==========================================================

def record_login_attempt(username):

    with get_connection() as conn:

        conn.execute("""
        INSERT INTO login_attempts (username, attempt_time)
        VALUES (?, ?)
        """, (username, datetime.now()))


def count_recent_attempts(username, minutes=10):

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT COUNT(*) as total
        FROM login_attempts
        WHERE username = ?
        AND attempt_time > datetime('now', ?)
        """, (username, f"-{minutes} minutes"))

        row = cur.fetchone()

        return row["total"]