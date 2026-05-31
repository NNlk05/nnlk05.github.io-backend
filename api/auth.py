import hmac
import hashlib
import base64
import json
from os import environ
from fastapi import Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional

SECRET_KEY = environ.get("SECRET_KEY", "b06d2c81c02d680b571f5d0a1633b9eb5fe80502")

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthUser(BaseModel):
    user_id: int
    username: str
    is_root: bool

def create_token(data: dict) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"

def verify_token(token: str) -> Optional[dict]:
    try:
        payload_str, signature = token.split(".")
        expected_signature = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        return json.loads(base64.urlsafe_b64decode(payload_str).decode())
    except Exception:
        return None

async def get_current_user(authorization: Optional[str] = Header(None)) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token: str = authorization.split(" ")[1]
    decoded = verify_token(token)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return AuthUser(
        user_id=decoded.get('user_id'),
        username=decoded.get('username'),
        is_root=decoded.get('is_root', False)
    )

def require_root(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.is_root:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Root access required"
        )
    return user

def require_owner_or_root(user_id: int, current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not current_user.is_root and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_user
