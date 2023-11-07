from db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.sql import func


# TODO: change Users class - DONE
class Users(Base):
    __tablename__ = 'users'

    email = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    

# TODO: change Transactions class - DONE
class Transactions(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("users.id"))
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    amount = Column(Integer)

