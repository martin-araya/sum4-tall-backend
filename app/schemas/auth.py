from pydantic import EmailStr
from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_name: str | None = None
    user_role: str | None = None


class RefreshRequest(BaseSchema):
    refresh_token: str
