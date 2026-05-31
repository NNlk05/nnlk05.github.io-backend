import hashlib
import secrets
from .db import DB
from typing import Optional, Dict, Any

class UserService:
    def __init__(self, db: DB) -> None:
        self.db: DB = db

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        return hash_obj.hexdigest(), salt

    def create_user(self, username: str, password: str, user_id: int) -> Dict[str, Any]:
        if self.db.find_one('users', username=username):
            raise ValueError("Username already exists")
        
        password_hash, salt = self._hash_password(password)
        user_data = {
            'id': user_id,
            'username': username,
            'password_hash': password_hash,
            'salt': salt
        }
        self.db.insert('users', user_data)
        return {'user_id': user_id, 'username': username}

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.db.find_one('users', id=user_id)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.db.find_one('users', username=username)

    def verify_password(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        hash_to_check, _ = self._hash_password(password, user['salt'])
        if hash_to_check == user['password_hash']:
            return user
        return None

    def update_user(self, user_id: int, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        update_data: Dict[str, Any] = {}
        if username:
            update_data['username'] = username
        if password:
            user = self.get_user(user_id)
            if not user:
                raise ValueError("User not found")
            password_hash, salt = self._hash_password(password)
            update_data['password_hash'] = password_hash
            update_data['salt'] = salt
        
        if update_data:
            self.db.update('users', {'id': user_id}, update_data)
        
        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> None:
        if not self.db.delete('users', id=user_id):
            raise ValueError("User not found")

    def list_all_users(self) -> list[Dict[str, Any]]:
        return self.db.find_all('users')
