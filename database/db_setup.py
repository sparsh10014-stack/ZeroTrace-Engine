import sqlite3


connection = sqlite3.connect("verification_logs.db")


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