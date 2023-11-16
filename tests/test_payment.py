import sys
sys.path.append('../src')
import unittest
from datetime import timedelta, datetime
from fastapi.testclient import TestClient
from src.routers.payment import create_test_payment
import pytest
from src.main import app
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from src.db.database import SessionLocal
from typing import Annotated, Any
from sqlalchemy.orm import Session
from src.routers.auth import create_access_token
import sqlalchemy

client = TestClient(app)
# These are used to create the signature for a JWT
SECRET_KEY = 'd17831803b0b0ab11c45452724e41ab3b88a4257c8656364be94275e58a41844'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

@pytest.fixture(autouse=True)
def before_each():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    debit_data = {
        "card_type": "debit",
        "card_number": 4532015112830366,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "balance": 5
    }
    client.post("/card/", json=debit_data, headers=headers)
    credit_data = {
        "card_type": "credit",
        "card_number": 4263982640269299,
        "expiration_month": 2,
        "expiration_year": 2026,
        "cvv": 837,
        "balance": 1
    }
    client.post("/card/", json=credit_data, headers=headers)

def get_test_token():
    test_username = "testuser"
    return create_access_token(test_username, 1, 'user', timedelta(minutes=30))

def test_process_payment():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "card_type": "debit",
        "card_number": 4532015112830366,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "amount": 0.5
    }
    # happy path
    assert client.post("/payment/", json=data, headers=headers).status_code == 202

    # card not found 
    data_card_not_found = {
        "card_type": "credit",
        "card_number": 5555555555554444,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "amount": 1
    }
    assert client.post("/payment/", json=data_card_not_found, headers=headers).status_code == 404

    data_invalid_type = {
        "card_type": "visa",
        "card_number": 4532015112830366,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "amount": 0.5
    }
    assert client.post("/payment/", json=data_invalid_type, headers=headers).status_code == 400

    data_invalid_num = {
        "card_type": "debit",
        "card_number": 4532015112830367,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "amount": 0.5
    }
    assert client.post("/payment/", json=data_invalid_num, headers=headers).status_code == 400

    data_expired = {
        "card_type": "credit",
        "card_number": 4532015112830366,
        "expiration_month": 1,
        "expiration_year": 2023,
        "cvv": 126,
        "amount": 0.1
    }
    assert client.post("/payment/", json=data_expired, headers=headers).status_code == 400

    data_match = {
        "card_type": "debit",
        "card_number": 4532015112830366,
        "expiration_month": 11,
        "expiration_year": 2026,
        "cvv": 126,
        "amount": 0.5 
    }
    assert client.post("/payment/", json=data_match, headers=headers).status_code == 400

    data_amount = {
        "card_type": "debit",
        "card_number": 4532015112830366,
        "expiration_month": 12,
        "expiration_year": 2026,
        "cvv": 126,
        "amount": 6.0
    }
    assert client.post("/payment/", json=data_amount, headers=headers).status_code == 400

    data_credit = {
        "card_type": "credit",
        "card_number": 4263982640269299,
        "expiration_month": 2,
        "expiration_year": 2026,
        "cvv": 837,
        "amount": 0.1
    }
    assert client.post("/payment/", json=data_credit, headers=headers).status_code == 202

def test_read_all():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    create_test_payment()

    response = client.get("/payment/read-all", headers=headers)
    assert response.status_code == 200
