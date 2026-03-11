from fastapi import APIRouter, Depends, status, HTTPException
from models.user import UserResponse
from sqlalchemy.orm import Session
from api.services import user as user_service
from db.database import get_db


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    users = user_service.get_all_users(db)
    return users


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


# @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
#     return user_service.create_user(db, user_create)


# @router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
# def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
#     user = user_service.update_user(db, user_id, user_update)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    is_deleted = user_service.delete_user(db, user_id)
    if not is_deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    return None
