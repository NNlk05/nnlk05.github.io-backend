from firebase_admin import auth
from .db import DB
from typing import Optional, Dict, Any

class UserService:
    def __init__(self, db: DB) -> None:
        self.db: DB = db

    def create_user(self, email: str, password: str, user_id: int) -> Dict[str, Any]:
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                uid=str(user_id)
            )
            self.db.insert('users', {
                'id': user_id,
                'email': email,
                'uid': user_record.uid
            })
            return {'user_id': user_id, 'email': email}
        except auth.EmailAlreadyExistsError:
            raise ValueError("Email already exists")
        except Exception as e:
            raise ValueError(f"Failed to create user: {str(e)}")

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.db.find_one('users', id=user_id)

    def update_user(self, user_id: int, email: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        try:
            if email:
                auth.update_user(str(user_id), email=email)
            if password:
                auth.update_user(str(user_id), password=password)
            
            update_data: Dict[str, Any] = {}
            if email:
                update_data['email'] = email
            
            self.db.update('users', {'id': user_id}, update_data)
            user = self.db.find_one('users', id=user_id)
            return user
        except Exception as e:
            raise ValueError(f"Failed to update user: {str(e)}")

    def delete_user(self, user_id: int) -> None:
        try:
            auth.delete_user(str(user_id))
            self.db.delete('users', id=user_id)
        except Exception as e:
            raise ValueError(f"Failed to delete user: {str(e)}")

    def list_all_users(self) -> list[Dict[str, Any]]:
        return self.db.find_all('users')
