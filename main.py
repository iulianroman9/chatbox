from fastapi import FastAPI
from api.routes import users
from db.database import engine
from db.models import Base

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(users.router)
