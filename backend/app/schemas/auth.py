from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    is_mfa_enabled: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    mfa_required: bool = False


class GoogleLoginRequest(BaseModel):
    token: str


class MFAVerifyRequest(BaseModel):
    code: str
