from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    user_id: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    is_root: bool

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
