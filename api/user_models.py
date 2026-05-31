from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    email: str
    is_root: bool

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
