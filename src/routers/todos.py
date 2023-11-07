from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session

from routers.auth import get_current_user
from routers.helpers import check_user_authentication

from models.models import Transactions
from db.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# when an API uses this, it will enforce authorization
user_dependency = Annotated[dict, (Depends(get_current_user))]


class Card(BaseModel):
    type: str
    number: str
    holder_name: str
    expiry_date: str
    cvv: int


class PaymentRequest(BaseModel):
    card: Card
    amount: int
    email: str


class DumpableTransaction(BaseModel):
    email: str
    amount: int


# TODO: refactor the payment_request to be dumpable, and change Transactions class - DONE
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def payment_processing(user: user_dependency, db: db_dependency, payment_request: PaymentRequest):
    check_user_authentication(user)
    # TODO: check card validity - Luhn Algorithm 
        # TODO: if failed in validation, reject request
    # TODO: check credit or debit card
        # TODO: if debit card - check enough funds for covering the purchase
    new_transaction = DumpableTransaction(email=payment_request.email, amount=payment_request.amount)
    transaction_model = Transactions(**new_transaction.model_dump())

    db.add(transaction_model)
    db.commit()

