import sqlite3
import pytest

from database.db_manager import insert_log, DATABASE_PATH


def test_database_has_exactly_three_columns():
    """Verify that the database contains only the required columns."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(verification_logs)")
        columns = cursor.fetchall()

        column_names = [column[1] for column in columns]

        assert column_names == [
            "Log_ID",
            "Timestamp",
            "Status"
        ]

    finally:
        connection.close()


def test_insert_pass():
    """Verify that PASS can be inserted."""

    insert_log("PASS")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT Status FROM verification_logs ORDER BY Log_ID DESC LIMIT 1"
        )

        result = cursor.fetchone()

        assert result[0] == "PASS"

    finally:
        connection.close()


def test_insert_fail():
    """Verify that FAIL can be inserted."""

    insert_log("FAIL")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT Status FROM verification_logs ORDER BY Log_ID DESC LIMIT 1"
        )

        result = cursor.fetchone()

        assert result[0] == "FAIL"

    finally:
        connection.close()


def test_invalid_status_is_rejected():
    """Verify that invalid statuses are rejected."""

    with pytest.raises(ValueError):
        insert_log("MAYBE")


def test_timestamp_is_generated():
    """Verify that SQLite automatically creates a timestamp."""

    insert_log("PASS")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT Timestamp
            FROM verification_logs
            ORDER BY Log_ID DESC
            LIMIT 1
            """
        )

        result = cursor.fetchone()

        assert result[0] is not None

    finally:
        connection.close()

def test_no_personal_information_columns():
    """Verify that no personal information columns exist."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(verification_logs)")
        columns = cursor.fetchall()

        column_names = {
            column[1].lower()
            for column in columns
        }

        forbidden_columns = {
            "name",
            "age",
            "address",
            "phone",
            "email",
            "location",
            "aadhaar"
        }

        assert column_names.isdisjoint(forbidden_columns)

    finally:
        connection.close()