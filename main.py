from fastapi import FastAPI
from api.lifespan import lifespan
from api.routes import users, auth, core

app = FastAPI(lifespan=lifespan)
app.include_router(core.router)
app.include_router(auth.router)
app.include_router(users.router)
