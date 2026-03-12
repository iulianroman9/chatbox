from fastapi import FastAPI
from api.lifespan import lifespan
from api.routes import auth_router, core_router, users_router, files_router

app = FastAPI(lifespan=lifespan)
app.include_router(core_router)
app.include_router(auth_router)
app.include_router(files_router)
app.include_router(users_router)
