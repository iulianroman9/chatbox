from sqlalchemy.orm import Session
from db.models import UserRecord
from models.user import UserCreate
from utils.security.hash import get_password_hash
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from db.database import get_db
import jwt
from jwt.exceptions import InvalidTokenError
from utils.config.config import settings
import api.services.user as user_service


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserRecord:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization.",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )
        user_id = int(user_id)
    except (InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token exception: {e}",
        )

    user = user_service.get_user(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )

    return user


def create_user(user_create: UserCreate, db: Session):
    pass_hash = get_password_hash(user_create.password)

    user = UserRecord(
        email=user_create.email,
        name=user_create.name,
        phone=user_create.phone,
        avatar_url=str(user_create.avatar_url) if user_create.avatar_url else None,
        password_hash=pass_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
