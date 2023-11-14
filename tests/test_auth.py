import unittest
from datetime import timedelta
from fastapi.testclient import TestClient
from src.main import app
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from src.db.database import SessionLocal
from typing import Annotated, Any
from sqlalchemy.orm import Session
from src.routers.auth import create_access_token, get_current_user
import sqlalchemy

client = TestClient(app)
# These are used to create the signature for a JWT
SECRET_KEY = 'd17831803b0b0ab11c45452724e41ab3b88a4257c8656364be94275e58a41844'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

def test_create_user():
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "surname": "User",
        "password": "testpassword",
        "role": "user"
    }
    try:
        response = client.post("/auth/", json=data)
        assert response.status_code == 201
    except sqlalchemy.exc.IntegrityError:
        pass

def test_login_for_access_token():
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/auth/token/", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()


if __name__ == '__main__':
    unittest.main()
