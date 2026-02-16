from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_admin: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class AdminPasswordReset(BaseModel):
    username: str
    new_password: str
