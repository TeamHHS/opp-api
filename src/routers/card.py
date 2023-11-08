# Card number for testing
{
  "card_type": "debit",
  "card_number": 4532015112830366,
  "expiration_month": 12,
  "expiration_year": 2026,
  "cvv": 126,
  "balance": 0
}

from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session

from routers.auth import get_current_user
from routers.helpers import check_user_authentication

from models.models import Cards
from db.database import SessionLocal

router = APIRouter(prefix='/card', tags=['card'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# when an API uses this, it will enforce authorization
user_dependency = Annotated[dict, (Depends(get_current_user))]

class CardsRequest(BaseModel):
    card_type: str
    card_number: int = Field(gt=999999999999999, lt=10000000000000000)
    expiration_month: int = Field(gt=0, lt=13)
    expiration_year: int = Field(gt=2023, lt=2033)
    cvv: int = Field(gt=99, lt=1000)
    balance: int

@router.get("/read-all")
async def read_all(user: user_dependency, db: db_dependency):
    check_user_authentication(user)
    return db.query(Cards).filter(Cards.owner_id == user.get('id')).all()


@router.get("/{card_number}", status_code=status.HTTP_200_OK)
async def read_card(user: user_dependency, db: db_dependency, card_number: int):
    check_user_authentication(user)

    card_model = (
        db.query(Cards).filter(Cards.card_number == card_number).filter(Cards.owner_id == user.get('id')).first()
    )

    if card_model is not None:
        return card_model
    raise HTTPException(status_code=404, detail='Card not found')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_card(user: user_dependency, db: db_dependency, card_request: CardsRequest):
    # Ensure user authentication
    check_user_authentication(user)

    # Check if a card with the same card number already exists
    existing_card = db.query(Cards).filter(Cards.card_number == card_request.card_number).filter(Cards.owner_id == user.get('id')).first()

    if existing_card:
        raise HTTPException(status_code=400, detail="Card with the same number already exists")

    card_model = Cards(**card_request.model_dump(), owner_id=user.get('id'))

    if not isValidType(card_model.card_type):
        raise HTTPException(status_code=400, detail="Invalid Card Type")
    elif not isValidNum(card_model.card_number):
        raise HTTPException(status_code=400, detail="Invalid Card Number")
    else:
        db.add(card_model)
    db.commit()


@router.put("/{card_number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_card(user: user_dependency, db: db_dependency,
                      card_request: CardsRequest,
                      card_number: int):
    # Ensure user authentication
    check_user_authentication(user)

    card_model = db.query(Cards).filter(Cards.card_number == card_number).filter(Cards.owner_id == user.get('id')).first()

    if card_model is None:  # Fix the variable name here
        raise HTTPException(status_code=404, detail="Card not found")

    # Update the card
    card_model.card_type = card_request.card_type
    card_model.expiration_month = card_request.expiration_month
    card_model.expiration_year = card_request.expiration_year
    card_model.cvv = card_request.cvv
    card_model.balance = card_request.balance

    if not isValidType(card_model.card_type):
        raise HTTPException(status_code=400, detail="Invalid Card Type")
    elif not isValidNum(card_model.card_number):
        raise HTTPException(status_code=400, detail="Invalid Card Number")
    else:
        db.add(card_model)
    db.commit()


@router.delete("/{card_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(user: user_dependency, db: db_dependency, card_number: int):
    # Ensure user authentication
    check_user_authentication(user)

    card_model = db.query(Cards).filter(Cards.card_number == card_number).filter(Cards.owner_id == user.get('id')).first()

    if card_model is None:
        raise HTTPException(status_code=404, detail="Card not found")

    db.query(Cards).filter(Cards.card_number == card_number).filter(Cards.owner_id == user.get('id')).delete()

    db.commit()

# Ensure card type is valid
async def isValidType(input):
    return input.lower() in ('debit', 'credit')

# Ensure card number is valid via Luhn Algorithm
async def isValidNum(num):
    # Convert the integer to a string
    num_str = str(num)
    if len(num_str) != 16:
        return False

    # Reverse the string and convert it back to an integer
    reversed_num = int(num_str[::-1])

    # Implement the Luhn algorithm
    total = 0
    double_digit = False
    for digit in str(reversed_num):
        if double_digit:
            doubled = int(digit) * 2
            total += doubled if doubled < 10 else (doubled - 9)
        else:
            total += int(digit)
        double_digit = not double_digit

    return total % 10 == 0