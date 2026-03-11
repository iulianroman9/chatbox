from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, min_length=5, max_length=50, strip=True)
    phone: str | None = Field(default=None)
    avatar_url: HttpUrl | None = Field(default=None, max_length=200)
    password: str = Field(min_length=8, max_length=64)


class UserUpdate(UserCreate):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=64)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str | None = None
    phone: str | None = None
    avatar_url: HttpUrl | str | None = None
    created_at: datetime
