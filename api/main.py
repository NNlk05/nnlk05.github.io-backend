from .db import DB
from .auth import get_current_user, require_root, require_owner_or_root, AuthUser, create_token
from .user_models import UserCreate, UserLogin, UserResponse, UserUpdate
from .user_service import UserService
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from os import environ
from .webhook import post_to_discord
from typing import List, Union

app: FastAPI = FastAPI()
db: DB = DB()
user_service: UserService = UserService(db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nnlk05.github.io",
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EditorDocument(BaseModel):
    id: str
    content: str

class DocumentResponse(BaseModel):
    id: str
    content: str

class DiscordMessage(BaseModel):
    content: str
    name: str

@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}

@app.post('/auth/signup', response_model=UserResponse)
def signup(user: UserCreate) -> UserResponse:
    db.create_collection('users')
    try:
        new_user = user_service.create_user(username=user.username, password=user.password)
        return UserResponse(user_id=new_user['user_id'], username=new_user['username'], is_root=new_user['user_id'] == 0)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/auth/login', response_model=dict)
def login(credentials: UserLogin) -> dict[str, Union[int, str]]:
    user = user_service.verify_password(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({
        "user_id": user['id'],
        "username": user['username'],
        "is_root": user['id'] == 0
    })
    return {"user_id": user['id'], "access_token": token, "token_type": "bearer"}

@app.get('/users/{user_id}', response_model=UserResponse)
def get_user(user_id: int) -> UserResponse:
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(user_id=user['id'], username=user['username'], is_root=user['id'] == 0)

@app.put('/users/{user_id}', response_model=UserResponse)
def update_user(user_id: int, update_data: UserUpdate, current_user: AuthUser = Depends(get_current_user)) -> UserResponse:
    require_owner_or_root(user_id, current_user)
    try:
        user = user_service.update_user(user_id, username=update_data.username, password=update_data.password)
        return UserResponse(user_id=user['id'], username=user['username'], is_root=user['id'] == 0)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete('/users/{user_id}', response_model=dict)
def delete_user(user_id: int, current_user: AuthUser = Depends(require_root)) -> dict[str, str]:
    try:
        user_service.delete_user(user_id)
        return {"status": "User deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/users', response_model=List[UserResponse])
def list_users(current_user: AuthUser = Depends(require_root)) -> List[UserResponse]:
    users = user_service.list_all_users()
    return [UserResponse(user_id=u['id'], username=u['username'], is_root=u['id'] == 0) for u in users]

@app.post('/documents')
def create_document(document: EditorDocument, current_user: AuthUser = Depends(get_current_user)) -> DocumentResponse:
    db.create_collection('documents')
    db.insert('documents', {
        'id': document.id,
        'content': document.content,
        'owner_id': current_user.user_id
    })
    return DocumentResponse(id=document.id, content=document.content)

@app.get('/documents/{document_id}')
def get_document(document_id: str, current_user: AuthUser = Depends(get_current_user)) -> DocumentResponse:
    doc: Union[dict, None] = db.find_one('documents', id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    if not current_user.is_root and doc.get('owner_id') != current_user.user_id:
        raise HTTPException(status_code=403, detail='Access denied')
    return DocumentResponse(id=doc['id'], content=doc['content'])

@app.post('/discord')
def send_discord_message(message: DiscordMessage) -> dict[str, str]:
    post_to_discord(content=message.content, name=message.name)
    return {"status": "ok"}

def main() -> None:
    import uvicorn
    production: bool = environ.get('PRODUCTION', 'false').lower() == 'true'
    if production:
        uvicorn.run('api.main:app', host='0.0.0.0', port=8000, workers=4)
    else:
        uvicorn.run('api.main:app', host='0.0.0.0', port=8000, reload=True)

if __name__ == '__main__':
    main()