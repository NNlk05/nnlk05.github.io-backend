from firebase_admin import auth
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthUser(BaseModel):
    user_id: int
    email: str
    is_root: bool

async def get_current_user(authorization: str = None) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    id_token: str = authorization.split(" ")[1]
    try:
        decoded: dict = auth.verify_id_token(id_token)
        email: str = decoded.get('email', '')
        user_id: int = int(decoded.get('uid', '0'))
        is_root: bool = user_id == 0
        return AuthUser(user_id=user_id, email=email, is_root=is_root)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
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
