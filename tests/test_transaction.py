import json
from fastapi.testclient import TestClient
from src.main import app
from src.routers.auth import create_access_token
from datetime import timedelta
import sqlalchemy
from datetime import datetime
from models.models import Payments 

client = TestClient(app)

def create_test_transaction(db):
    transaction_data = {
        "card": 1234567890123456,
        "amount": 50.0,
        "complete": True,
        "owner_id": 1,
        "card_type": "debit"
    }
    transaction = Payments(**transaction_data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction.id

def get_test_token():
    test_username = "testuser"
    return create_access_token(test_username, 1, "user", timedelta(minutes=30))

def test_get_total_balance():
    # Obtain a valid token
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/transaction/total-balance", headers=headers)
    assert response.status_code == 200
    total_balance = response.json()
    assert isinstance(total_balance, float)

def test_get_total_balance_period():
    # Obtain a valid token
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    start_date = "2023-01-01T00:00:00Z"
    end_date = "2023-12-31T23:59:59Z"
    response = client.get(f"/transaction/total-balance/{start_date}/{end_date}", headers=headers)
    assert response.status_code == 200
    total_balance_period = response.json()
    assert isinstance(total_balance_period, float)

# def test_get_all_transactions(db):  # Include the db fixture as a parameter
#     # Assuming you have some logic to create a test transaction
#     # For example, you might have a function create_test_transaction(db) that adds a transaction to the database
    
#     # Call the function to create a test transaction
#     create_test_transaction(db)
    
#     # Obtain a valid token
#     token = get_test_token()
#     headers = {"Authorization": f"Bearer {token}"}

#     # Assuming you have some completed transactions for the user
#     response = client.get("/transaction/all-transactions", headers=headers)
    
#     # Assuming the endpoint should return a 200 status code when there are transactions
#     assert response.status_code == 200

def test_get_accounts_receivables():
    # Obtain a valid token
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/transaction/accounts-receivables", headers=headers)
    assert response.status_code == 200
    accounts_receivables = response.json()
    assert isinstance(accounts_receivables, list)

def test_get_accounts_receivables_no_pending_transactions():
    # Obtain a valid token
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/transaction/accounts-receivables", headers=headers)
    assert response.status_code == 200
    accounts_receivables = response.json()
    assert len(accounts_receivables) == 0

def test_get_total_balance_invalid_token():
    # Assuming an invalid token
    invalid_token = 'invalid_token'
    response = client.get("/transaction/total-balance", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401

def test_get_total_balance_period_invalid_token():
    invalid_token = 'invalid_token'
    start_date = "2023-01-01T00:00:00Z"
    end_date = "2023-12-31T23:59:59Z"
    response = client.get(f"/transaction/total-balance/{start_date}/{end_date}", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401