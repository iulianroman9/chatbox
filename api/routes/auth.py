from fastapi import APIRouter, status, Depends, HTTPException
from models.user import UserCreate, UserResponse, UserLogin
from models.token import TokenResponse
from sqlalchemy.orm import Session
from db.database import get_db
from api.services import user as user_service
from api.security.jwt_token import create_access_token
from api.security.hash import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, user_login.email)

    if not existing_user or not verify_password(
        user_login.password, existing_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token({"sub": existing_user.id})
    user = UserResponse.model_validate(existing_user)

    return TokenResponse(user=user, access_token=access_token)


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
    user = UserResponse.model_validate(user)

    access_token = create_access_token({"sub": user.id})

    return TokenResponse(user=user, access_token=access_token)
