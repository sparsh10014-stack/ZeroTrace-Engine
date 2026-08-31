import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# =========================================================
# BASIC API VALIDATION
# =========================================================

def test_empty_request(client):
    response = client.post("/api/issue-credential", json={})

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


def test_missing_citizen_id(client):
    response = client.post(
        "/api/issue-credential",
        json={
            "some_other_field": "test"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


# =========================================================
# CITIZEN DATABASE VALIDATION
# =========================================================

def test_unknown_citizen_returns_404(client):
    response = client.post(
        "/api/issue-credential",
        json={
            "ocr_id_hash": "DOES_NOT_EXIST"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_valid_citizen_reaches_issuer(client):
    response = client.post(
        "/api/issue-credential",
        json={
            "ocr_id_hash": "234868130985"
        }
    )

    assert response.status_code in [200, 500]

    data = response.get_json()

    assert data is not None


# =========================================================
# REVOKED CITIZEN VALIDATION
# =========================================================

def test_revoked_citizen_returns_403(client):
    response = client.post(
        "/api/issue-credential",
        json={
            "ocr_id_hash": "641158019058"
        }
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["success"] is False
    assert "revoked" in data["message"].lower()

# =========================================================
# FRONTEND COMPATIBILITY
# =========================================================

def test_frontend_parameter_name_is_supported(client):
    response = client.post(
        "/api/issue-credential",
        json={
            "ocr_id_hash": "DOES_NOT_EXIST"
        }
    )

    # Frontend currently sends ocr_id_hash.
    # The API must recognize it and reach database lookup.
    assert response.status_code == 404


def test_alternative_parameter_name_is_supported(client):
    response = client.post(
        "/api/issue-credential",
        json={
            "ocr_id_number": "DOES_NOT_EXIST"
        }
    )

    # Backend currently supports both parameter names.
    assert response.status_code == 404