from fastapi import FastAPI
import sys

from models import models
from db.database import engine
from routers import auth, payment, admin, card, transaction

sys.path.append("/Users/sbt/Desktop/CS5500/opp-api/src")

# application
app = FastAPI()

# sets up database defined in engine
models.Base.metadata.create_all(bind=engine)

# Set API endpoints on router
app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(card.router)
app.include_router(admin.router)
app.include_router(transaction.router)
