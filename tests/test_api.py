import requests


BASE_URL = "http://127.0.0.1:5000"


def test_empty_request():
    response = requests.post(
        f"{BASE_URL}/verify",
        json={}
    )

    assert response.status_code == 400


def test_missing_proof():
    response = requests.post(
        f"{BASE_URL}/verify",
        json={
            "publicSignals": []
        }
    )

    assert response.status_code == 400


def test_missing_public_signals():
    response = requests.post(
        f"{BASE_URL}/verify",
        json={
            "proof": {}
        }
    )

    assert response.status_code == 400