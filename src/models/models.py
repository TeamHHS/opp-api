from db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.sql import func


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    surname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


class Cards(Base):
    __tablename__ = "cards"

    card_type = Column(String, nullable=False)
    card_number = Column(Integer, nullable=False, primary_key=True, index=True)
    expiration_month = Column(Integer, nullable=False)
    expiration_year = Column(Integer, nullable=False)
    cvv = Column(Integer, nullable=False)
    balance = Column(Float, default=100)
    owner_id = Column(Integer, ForeignKey("users.id"))


class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    card = Column(Integer, nullable=False)
    card_type = Column(String, nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    complete = Column(Boolean, nullable=False)
    amount = Column(Float, nullable=False)


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    complete = Column(Boolean, nullable=False)
    amount = Column(Float, nullable=False)
