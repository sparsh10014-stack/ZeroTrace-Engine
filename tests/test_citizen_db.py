import sqlite3

import database.citizen_db as citizen_db


def create_test_database(tmp_path):
    db_path = tmp_path / "test_citizens.db"

    conn = sqlite3.connect(db_path)

    conn.execute("""
        CREATE TABLE citizens (
            id_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            active INTEGER NOT NULL CHECK (active IN (0, 1))
        )
    """)

    conn.executemany("""
        INSERT INTO citizens
        (id_number, name, date_of_birth, active)
        VALUES (?, ?, ?, ?)
    """, [
        ("TEST001", "Test Active", "2000-01-01", 1),
        ("TEST002", "Test Revoked", "1995-01-01", 0),
    ])

    conn.commit()
    conn.close()

    return db_path


def test_revoke_active_citizen(tmp_path, monkeypatch):
    db_path = create_test_database(tmp_path)

    monkeypatch.setattr(citizen_db, "DB_PATH", db_path)

    result = citizen_db.revoke_citizen("TEST001")

    assert result is True

    citizen = citizen_db.get_citizen_by_id("TEST001")

    assert citizen["active"] is False


def test_revoke_unknown_citizen(tmp_path, monkeypatch):
    db_path = create_test_database(tmp_path)

    monkeypatch.setattr(citizen_db, "DB_PATH", db_path)

    result = citizen_db.revoke_citizen("DOES_NOT_EXIST")

    assert result is False


def test_revoke_already_revoked_citizen(tmp_path, monkeypatch):
    db_path = create_test_database(tmp_path)

    monkeypatch.setattr(citizen_db, "DB_PATH", db_path)

    result = citizen_db.revoke_citizen("TEST002")

    assert result is False

    citizen = citizen_db.get_citizen_by_id("TEST002")

    assert citizen["active"] is False