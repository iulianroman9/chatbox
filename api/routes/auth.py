from fastapi import APIRouter, status, Depends, HTTPException
from models.user import UserCreate, UserResponse
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
    existing_user = user_service.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already in use.",
        )

    user = user_service.create_user(db, user_create)
    access_token = "fake token"

    return {"user": UserResponse.model_validate(user), "access_token": access_token}
