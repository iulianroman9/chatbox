from pydantic import BaseModel
from .user import UserResponse


class TokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
