from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    password: str


class UserUpdate(UserCreate):
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    created_at: datetime
