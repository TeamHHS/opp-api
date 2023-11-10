# Card number for testing
{
  "card_type": "debit",
  "card_number": 4532015112830366,
  "expiration_month": 12,
  "expiration_year": 2026,
  "cvv": 126,
  "amount": 1
}

{
  "card_type": "credit",
  "card_number": 5555555555554444,
  "expiration_month": 12,
  "expiration_year": 2026,
  "cvv": 126,
  "amount": 1
}

from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from routers.auth import get_current_user
from routers.helpers import check_user_authentication
from routers.card import isValidType, isValidNum, isExpired

from models.models import Payments, Cards
from db.database import SessionLocal

from datetime import timedelta

router = APIRouter(prefix='/payment', tags=['payment'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# when an API uses this, it will enforce authorization
user_dependency = Annotated[dict, (Depends(get_current_user))]

class PaymentRequest(BaseModel):
    card_number: int = Field(gt=999999999999999, lt=10000000000000000)
    expiration_month: int = Field(gt=0, lt=13)
    expiration_year: int = Field(gt=2023, lt=2033)
    cvv: int = Field(gt=99, lt=1000)
    card_type: str
    amount: float

@router.get("/read-all")
async def read_all(user: user_dependency, db: db_dependency):
    check_user_authentication(user)
    update_payment_status(user, db)
    return db.query(Payments).filter(Payments.owner_id == user.get('id')).all()

# Assumption is that UI make appropriate request after checking card type and card validity
@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def process_payment(user: user_dependency, db: db_dependency, payment_request: PaymentRequest):
    check_user_authentication(user)

    card_model = (
        db.query(Cards).filter(Cards.card_number == payment_request.card_number).filter(Cards.owner_id == user.get('id')).first()
    )

    if card_model is None:
        raise HTTPException(status_code=404, detail="Card not found")
    
    if not isValidType(card_model.card_type):
        raise HTTPException(status_code=400, detail="Invalid Card Type")
    elif not isValidNum(card_model.card_number):
        raise HTTPException(status_code=400, detail="Invalid Card Number")
    elif isExpired(card_model.expiration_month, card_model.expiration_year):
        raise HTTPException(status_code=400, detail="Expired Card")

    if card_model.expiration_month != payment_request.expiration_month or \
        card_model.expiration_year != payment_request.expiration_year or \
        card_model.cvv != payment_request.cvv or \
        card_model.card_type != payment_request.card_type:
        raise HTTPException(status_code=400, detail="Card info is not correct")
        
    if card_model.card_type == 'debit' and card_model.balance < payment_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance on card")

    complete_status = True
    if card_model.card_type == 'credit':
        complete_status = False
    card_model.balance -= payment_request.amount

    payment_model = Payments(card=card_model.card_number,
                             card_type=card_model.card_type, 
                             amount=payment_request.amount, 
                             complete=complete_status, 
                             owner_id=user.get("id"))

    db.add(card_model)
    db.add(payment_model)
    db.commit()

def update_payment_status(user: user_dependency, db: db_dependency):
    for payment_model in db.query(Payments).filter(Payments.owner_id == user.get('id')).all():
        if payment_model and payment_model.card_type == 'credit':
            current_db_time = db.query(func.now()).scalar()

            if current_db_time > payment_model.payment_date + timedelta(seconds=20):
                payment_model.complete = True
                db.add(payment_model)
    db.commit()
