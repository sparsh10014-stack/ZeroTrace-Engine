import sqlite3


DB_PATH = "database/zerotrace.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_citizen_by_id(citizen_id):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT id, name, dob, active
            FROM citizens
            WHERE id = ?
            """,
            (citizen_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def is_credential_active(citizen_id):
    citizen = get_citizen_by_id(citizen_id)

    if citizen is None:
        return False

    return bool(citizen["active"])