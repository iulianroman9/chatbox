from fastapi import APIRouter, Depends
from db.models import UserRecord
from api.services.auth import get_current_user

router = APIRouter(tags=["Core"])


@router.get("/")
def root(user: UserRecord = Depends(get_current_user)):
    return {
        "message": "Chatbox API is running ok.",
        "version": "0.1.0",
        "user_name": user.name,
    }


@router.get("/healthz")
def healthz():
    return {"status": "ok"}
