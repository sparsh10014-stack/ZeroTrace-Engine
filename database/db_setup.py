import sqlite3
from pathlib import Path


DATABASE_FOLDER = Path(__file__).resolve().parent

DATABASE_PATH = DATABASE_FOLDER / "verification_logs.db"

connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_logs (
        Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        Status TEXT NOT NULL CHECK (Status IN ('PASS', 'FAIL'))
    )
""")

connection.commit()

connection.close()

print("Database setup completed successfully.")
print(f"Database location: {DATABASE_PATH}")