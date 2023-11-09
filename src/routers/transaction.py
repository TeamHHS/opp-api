from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime, timedelta
from pydantic import BaseModel
from models.models import Payments
from db.database import SessionLocal
from routers.auth import get_current_user
from routers.helpers import check_user_authentication

router = APIRouter(prefix='/transaction', tags=['transaction'])

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
        
        # Calculate total balance of fully processed funds
        total_balance = db.query(Payments).filter(
            Payments.owner_id == user.get('id'),
            Payments.complete == True
        ).with_entities(Payments.amount).scalar() or 0.0
        
        return total_balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/total-balance/{start_date}/{end_date}", response_model=float)
async def get_total_balance_period(
    user: user_dependency, 
    db: db_dependency,
    start_date: datetime,
    end_date: datetime
):
    try:
        check_user_authentication(user)
        
        # Calculate total balance of fully processed funds for a certain time period
        total_balance_period = db.query(Payments).filter(
            Payments.owner_id == user.get('id'),
            Payments.complete == True,
            Payments.transaction_date.between(start_date, end_date)
        ).with_entities(Payments.amount).scalar() or 0.0
        
        return total_balance_period
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-transactions", response_model=List[PaymentsResponse])
async def get_all_transactions(user: user_dependency, db: db_dependency):
    try:
        check_user_authentication(user)
        
        # Get a list of all transactions that comprise the total balance
        all_transactions = db.query(Payments).filter(
            Payments.owner_id == user.get('id'),
            Payments.complete == True
        ).all()
        
        # Convert Payments objects to PaymentsResponse objects
        transactions_response = [
            PaymentsResponse(
                card=transaction.card,
                amount=transaction.amount,
                complete=transaction.complete,
                owner_id=transaction.owner_id
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
        
        # Get a list of all accounts receivables (pending purchases)
        accounts_receivables = db.query(Payments).filter(
            Payments.owner_id == user.get('id'),
            Payments.complete == False
        ).all()
        
        return accounts_receivables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
