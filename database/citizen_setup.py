import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "citizens.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            id_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            active INTEGER NOT NULL CHECK (active IN (0, 1))
        )
    """)
    conn.commit()
    conn.close()

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear out the dummy data to ensure a clean slate for the real demo
    cursor.execute("DELETE FROM citizens")

    # Insert the real team data. 
    # Replace the placeholder strings with the actual 12-digit Aadhaar numbers.
    citizens = [
        ("234868130985", "Sparsh Pathak", "2005-09-12", 1),
        ("641158019058", "Prakhar Srivastav", "2005-05-28", 1),    # Update with Sachin's real DOB
        # ("RITIK_12_DIGIT_AADHAAR", "Ritik", "2005-08-14", 1),      # Update with Ritik's real DOB
        # ("SNEHLATA_12_DIGIT_AADHAAR", "Snehlata", "2005-11-03", 1) # Update with Snehlata's real DOB
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO citizens
        (id_number, name, date_of_birth, active)
        VALUES (?, ?, ?, ?)
    """, citizens)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    seed_database()
    print("Real Team Aadhaar database created and seeded successfully.")