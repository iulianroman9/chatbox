from sqlalchemy.orm import Session
from db.models import UserRecord
from schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int):
    return db.query(UserRecord).filter(UserRecord.id == user_id).first()


def get_all_users(db: Session):
    return db.query(UserRecord).all()


def create_user(db: Session, user_in: UserCreate):
    not_hashed_password = user_in.password

    db_user = UserRecord(
        email=user_in.email,
        name=user_in.name,
        phone=user_in.phone,
        avatar_url=user_in.avatar_url,
        password_hash=not_hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(db: Session, user_id: int, user_in: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        new_password = update_data.pop("password")
        update_data["password_hash"] = new_password

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
