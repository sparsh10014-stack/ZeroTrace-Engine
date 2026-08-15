import sqlite3
from pathlib import Path


DATABASE_FOLDER = Path(__file__).resolve().parent

DATABASE_PATH = DATABASE_FOLDER / "verification_logs.db"

def insert_log(status):
    """
    Insert a verification result into the database.

    status must be either 'PASS' or 'FAIL'.
    """

    if status not in ("PASS", "FAIL"):
        raise ValueError("Status must be either 'PASS' or 'FAIL'.")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO verification_logs (Status) VALUES (?)",
            (status,)
        )

        connection.commit()

    finally:
        connection.close()