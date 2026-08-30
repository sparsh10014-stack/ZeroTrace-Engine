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

    citizens = [
        ("CITIZEN001", "Rahul Sharma", "1998-04-12", 1),
        ("CITIZEN002", "Priya Singh", "2000-07-25", 1),
        ("CITIZEN003", "Amit Verma", "2010-03-18", 1),
        ("CITIZEN004", "Neha Gupta", "1995-11-03", 1),
        ("CITIZEN005", "Rohit Kumar", "2008-09-14", 1),
        ("CITIZEN006", "Anjali Yadav", "1999-01-30", 1),
        ("CITIZEN007", "Vikas Chauhan", "1997-06-21", 1),
        ("CITIZEN008", "Pooja Singh", "2011-12-05", 1),
        ("CITIZEN009", "Arjun Mehta", "1996-02-17", 1),
        ("CITIZEN010", "Simran Kaur", "2001-08-09", 1),

        # Deliberately revoked citizen for testing
        ("CITIZEN011", "Karan Malhotra", "1994-05-26", 0),

        ("CITIZEN012", "Sneha Sharma", "2002-10-15", 1),
        ("CITIZEN013", "Manish Patel", "1993-03-08", 1),
        ("CITIZEN014", "Kavya Joshi", "2009-07-19", 1),
        ("CITIZEN015", "Deepak Singh", "1991-09-27", 1),
        ("CITIZEN016", "Riya Verma", "2003-04-11", 1),
        ("CITIZEN017", "Saurabh Gupta", "1990-12-22", 1),
        ("CITIZEN018", "Nisha Kumari", "2007-06-16", 1),
        ("CITIZEN019", "Aditya Raj", "1999-02-28", 1),
        ("CITIZEN020", "Meera Kapoor", "2004-11-13", 1),
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
    print("Citizen database created and seeded successfully.")