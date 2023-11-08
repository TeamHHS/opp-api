from db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    surname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Cards(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, index=True)
    card_type = Column(String, nullable=False)
    card_number = Column(Integer, nullable=False)
    expiration_month = Column(Integer, nullable=False)
    expiration_year = Column(Integer, nullable=False)
    cvv = Column(Integer, nullable=False)
    balance = Column(Float, default=100)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    pending = Column(Boolean, nullable=False)
    amount = Column(Integer, nullable=False)

class GenericObject(Base):
    __tablename__ = 'generics'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)







