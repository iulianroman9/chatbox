from sqlalchemy.orm import Session
from db.models import UserRecord
from models.user import UserCreate, UserUpdate
from api.security.hash import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(UserRecord).filter(UserRecord.email == email).first()


def get_user(db: Session, user_id: int):
    return db.query(UserRecord).filter(UserRecord.id == user_id).first()


def get_all_users(db: Session):
    return db.query(UserRecord).all()


def create_user(db: Session, user_create: UserCreate):
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


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        new_password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(new_password)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
