import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "citizens.db"


def get_citizen_by_id(id_number):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_number, name, date_of_birth, active
        FROM citizens
        WHERE id_number = ?
    """, (id_number,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "id_number": row["id_number"],
        "name": row["name"],
        "date_of_birth": row["date_of_birth"],
        "active": bool(row["active"])
    }

def revoke_citizen(id_number):
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE citizens
        SET active = 0
        WHERE id_number = ?
        AND active = 1
    """, (id_number,))

    updated_rows = cursor.rowcount

    conn.commit()
    conn.close()

    return updated_rows == 1