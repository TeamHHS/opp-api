# format for timestamp: 2023-11-09T10:40:52Z

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from models.models import Payments
from db.database import SessionLocal
from routers.auth import get_current_user
from routers.helpers import check_user_authentication
from routers.payment import update_payment_status
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import func

router = APIRouter(prefix="/transaction", tags=["transaction"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, (Depends(get_current_user))]


class PaymentsResponse(BaseModel):
    card: int
    amount: float
    complete: bool
    owner_id: int


@router.get("/total-balance", response_model=float)
async def get_total_balance(user: user_dependency, db: db_dependency):
    try:
        check_user_authentication(user)
        update_payment_status(user, db)

        # Calculate total balance of fully processed funds
        total_balance = (
            db.query(func.sum(Payments.amount))
            .filter(Payments.owner_id == user.get("user_id"), Payments.complete == True)
            .scalar()
            or 0.0
        )

        return total_balance
    except MultipleResultsFound as e:
        print("Multiple rows found:", e)
        return None
    except NoResultFound as e:
        print("No rows found:", e)
        return None


@router.get("/total-balance/{start_date}/{end_date}", response_model=float)
async def get_total_balance_period(
    user: user_dependency, db: db_dependency, start_date: datetime, end_date: datetime
):
    try:
        check_user_authentication(user)
        update_payment_status(user, db)

        # Calculate total balance of fully processed funds
        total_balance = (
            db.query(func.sum(Payments.amount))
            .filter(
                Payments.owner_id == user.get("user_id"),
                Payments.complete == True,
                Payments.payment_date.between(start_date, end_date),
            )
            .scalar()
            or 0.0
        )

        return total_balance
    except MultipleResultsFound as e:
        print("Multiple rows found:", e)
        return None
    except NoResultFound as e:
        print("No rows found:", e)
        return None


@router.get("/all-transactions", response_model=List[PaymentsResponse])
async def get_all_transactions(user: user_dependency, db: db_dependency):
    try:
        check_user_authentication(user)
        update_payment_status(user, db)

        # Get a list of all transactions that comprise the total balance
        all_transactions = (
            db.query(Payments)
            .filter(Payments.owner_id == user.get("user_id"), Payments.complete == True)
            .all()
        )

        # Convert Payments objects to PaymentsResponse objects
        transactions_response = [
            PaymentsResponse(
                card=transaction.card,
                amount=transaction.amount,
                complete=transaction.complete,
                owner_id=transaction.owner_id,
            )
            for transaction in all_transactions
        ]

        return transactions_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts-receivables", response_model=List[PaymentsResponse])
async def get_accounts_receivables(user: user_dependency, db: db_dependency):
    try:
        check_user_authentication(user)
        update_payment_status(user, db)

        # Get a list of all accounts receivables (pending purchases)
        accounts_receivables = (
            db.query(Payments)
            .filter(
                Payments.owner_id == user.get("user_id"), Payments.complete == False
            )
            .all()
        )

        return accounts_receivables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
