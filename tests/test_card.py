from fastapi.testclient import TestClient
from src.main import app
from src.routers.auth import create_access_token
from datetime import timedelta

client = TestClient(app)


def get_test_token():
    test_username = "testuser"
    return create_access_token(test_username, 1, "user", timedelta(minutes=30))


def test_create_card():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "card_type": "debit",
        "card_number": 4532015112830366,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "balance": 5,
    }
    try:
        response = client.post("/card/", json=data, headers=headers)
        assert response.status_code == 201

    # If card is already in the database
    except Exception:
        assert response.status_code == 400


def test_read_all_cards():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/card/read-all", headers=headers)
    assert response.status_code == 200


def test_read_card():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    existing_card_number = 4532015112830366
    response = client.get(f"/card/{existing_card_number}", headers=headers)
    assert response.status_code == 200

    # If card number is not in database
    response = client.get("/card/1234567890123456", headers=headers)
    assert response.status_code == 404


def test_update_card():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "card_type": "debit",
        "card_number": 4532015112830366,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "balance": 5,
    }
    existing_card_number = 4532015112830366
    response = client.put(
        f"/card/{existing_card_number}", json=update_data, headers=headers
    )
    assert response.status_code == 204
    response = client.put("/card/1234567890123456", json=update_data, headers=headers)
    assert response.status_code == 404


def test_delete_card():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    existing_card_number = 4532015112830366
    response = client.delete(f"/card/{existing_card_number}", headers=headers)
    assert response.status_code == 204
    response = client.delete("/card/1234567890123456", headers=headers)
    assert response.status_code == 404
