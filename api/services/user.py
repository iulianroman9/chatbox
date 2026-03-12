from sqlalchemy.orm import Session
from db.models import UserRecord
from models.user import UserUpdate
from utils.security.hash import get_password_hash


def get_user_by_email(email: str, db: Session):
    return db.query(UserRecord).filter(UserRecord.email == email).first()


def get_user(user_id: int, db: Session):
    return db.query(UserRecord).filter(UserRecord.id == user_id).first()


def get_all_users(db: Session):
    return db.query(UserRecord).all()


def update_user(user_id: int, user_update: UserUpdate, db: Session):
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


def delete_user(user_id: int, db: Session):
    user = get_user(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
