from fastapi import APIRouter, status, Depends
from models.user import UserCreate
from models.token import TokenResponse
from sqlalchemy.orm import Session
from db.database import get_db
from api.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    pass


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_create)
