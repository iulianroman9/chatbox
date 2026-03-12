from fastapi import APIRouter, status, HTTPException, Depends
from models.user import UserCreate, UserResponse, UserLogin
from models.token import TokenResponse
from api.services import user as user_service
from api.services import auth as auth_service
from utils.security.jwt_token import create_access_token
from utils.security.hash import verify_password
from db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(user_login.email, db)

    if not existing_user or not verify_password(
        user_login.password, existing_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token({"sub": str(existing_user.id)})
    user = UserResponse.model_validate(existing_user)

    return TokenResponse(user=user, access_token=access_token)


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(user_create.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already in use.",
        )

    user = auth_service.create_user(user_create, db)
    user = UserResponse.model_validate(user)

    access_token = create_access_token({"sub": str(user.id)})

    return TokenResponse(user=user, access_token=access_token)
