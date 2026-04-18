# ==========================================================
# ANALYTICS ENGINE
# ADMIN DASHBOARD DATA
# ==========================================================

from database import get_connection


# ==========================================================
# TOTAL USERS
# ==========================================================

def total_users():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT COUNT(*) as total
        FROM users
        """)

        row = cur.fetchone()

        return row["total"]


# ==========================================================
# TOTAL DOWNLOADS
# ==========================================================

def total_downloads():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT COUNT(*) as total
        FROM downloads
        """)

        row = cur.fetchone()

        return row["total"]


# ==========================================================
# ACTIVE USERS
# (users who downloaded at least one file)
# ==========================================================

def active_users():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT COUNT(DISTINCT username) as total
        FROM downloads
        """)

        row = cur.fetchone()

        return row["total"]


# ==========================================================
# DOWNLOADS PER USER
# ==========================================================

def downloads_per_user():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT username, COUNT(*) as total
        FROM downloads
        GROUP BY username
        ORDER BY total DESC
        """)

        rows = cur.fetchall()

        labels = []
        values = []

        for r in rows:

            labels.append(r["username"])
            values.append(r["total"])

        return {
            "labels": labels,
            "values": values
        }


# ==========================================================
# DOWNLOADS PER DAY
# ==========================================================

def downloads_per_day():

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT DATE(timestamp) as day,
               COUNT(*) as total
        FROM downloads
        GROUP BY day
        ORDER BY day ASC
        """)

        rows = cur.fetchall()

        labels = []
        values = []

        for r in rows:

            labels.append(r["day"])
            values.append(r["total"])

        return {
            "labels": labels,
            "values": values
        }


# ==========================================================
# MOST DOWNLOADED FILES
# ==========================================================

def top_files(limit=10):

    with get_connection() as conn:

        cur = conn.execute("""
        SELECT file_name, COUNT(*) as total
        FROM downloads
        GROUP BY file_name
        ORDER BY total DESC
        LIMIT ?
        """, (limit,))

        rows = cur.fetchall()

        labels = []
        values = []

        for r in rows:

            labels.append(r["file_name"])
            values.append(r["total"])

        return {
            "labels": labels,
            "values": values
        }


# ==========================================================
# ADMIN SUMMARY
# ==========================================================

def dashboard_summary():

    return {

        "total_users": total_users(),

        "total_downloads": total_downloads(),

        "active_users": active_users()

    }