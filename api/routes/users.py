from fastapi import APIRouter
from api.schemas.user import UserCreate, UserResponse, UserUpdate


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def get_all_users():
    pass


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    pass


@router.post("/", response_model=UserResponse)
def create_user(user_create: UserCreate):
    pass


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate):
    pass


@router.delete("/{user_id}")
def delete_user(user_id: int):
    pass
