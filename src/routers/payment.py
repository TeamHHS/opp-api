from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session

from routers.auth import get_current_user
from routers.helpers import check_user_authentication

from models.models import Payments, Cards
from db.database import SessionLocal

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
    amount: float

@router.get("/read-all")
async def read_all(user: user_dependency, db: db_dependency):
    check_user_authentication(user)
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

    if card_model.expiration_month != payment_request.expiration_month or \
        card_model.expiration_year != payment_request.expiration_year or \
        card_model.cvv != payment_request.cvv:
        raise HTTPException(status_code=400, detail="Card info is not correct")
        
    if card_model.card_type == 'debit' and card_model.balance < payment_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance on card")

    complete_status = True
    if card_model.card_type == 'credit':
        complete_status = False
    card_model.balance -= payment_request.amount

    payment_model = Payments(card=card_model.card_number, 
                             amount=payment_request.amount, 
                             complete=complete_status, 
                             owner_id=user.get("id"))

    db.add(card_model)
    db.add(payment_model)
    db.commit()
