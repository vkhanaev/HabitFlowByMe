from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.types import Password


class RegisterRequest(BaseModel):
    email: EmailStr
    password: Password


class UserResponse(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
