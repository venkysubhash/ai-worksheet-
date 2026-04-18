# ==========================================================
# RATE LIMITER
# PROTECTS LOGIN FROM BRUTE FORCE ATTACKS
# ==========================================================

from datetime import datetime, timedelta
from fastapi import HTTPException
from database import record_login_attempt, count_recent_attempts

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------

MAX_ATTEMPTS = 5
WINDOW_MINUTES = 10


# ----------------------------------------------------------
# CHECK IF LOGIN IS ALLOWED
# ----------------------------------------------------------

def check_login_allowed(username: str):

    attempts = count_recent_attempts(username, WINDOW_MINUTES)

    if attempts >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again later."
        )


# ----------------------------------------------------------
# RECORD FAILED LOGIN
# ----------------------------------------------------------

def record_failed_login(username: str):

    record_login_attempt(username)


# ----------------------------------------------------------
# RESET LOGIN ATTEMPTS (OPTIONAL)
# ----------------------------------------------------------

def reset_attempts(username: str):

    """
    Optional utility if you want to clear attempts after
    a successful login.
    """

    from database import get_connection

    with get_connection() as conn:

        conn.execute("""
        DELETE FROM login_attempts
        WHERE username = ?
        """, (username,))