from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session

from routers.auth import get_current_user
from routers.helpers import check_user_authentication

from models.models import Transactions, Cards
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
    card_id: int
    amount: int
    pending: bool

# Assumption is that UI make appropriate request after checking card type and card validity
@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def process_payment(user: user_dependency, db: db_dependency, payment_request: PaymentRequest):
    check_user_authentication(user)

    card_model = (
        db.query(Cards).filter(Cards.id == payment_request.card_id).filter(Cards.owner_id == user.get('id')).first()
    )

    if card_model.balance < payment_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance on card")

    card_model.balance -= payment_request.amount
    transaction_model = Transactions(amount=payment_request.amount, pending=payment_request.pending, owner_id=user.get("id"))

    db.add(card_model)
    db.add(transaction_model)
    db.commit()
