from .db import DB
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from os import environ
from .webhook import post_to_discord
from requests import HTTPError
from time import sleep

app: FastAPI = FastAPI()
db: DB = DB()

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
def root():
    return {"status": "ok"}

@app.post('/documents')
def create_document(document: EditorDocument) -> DocumentResponse:
    db.create_collection('documents')
    db.insert('documents', {
        'id': document.id,
        'content': document.content
    })
    return DocumentResponse(id=document.id, content=document.content)

@app.get('/documents/{document_id}')
def get_document(document_id: str) -> DocumentResponse:
    doc: dict | None = db.find_one('documents', id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return DocumentResponse(id=doc['id'], content=doc['content'])

@app.post('/discord')
def send_discord_message(request: Request, message: DiscordMessage) -> dict:
    message.content = message.content + f"\n Headers: \n```{len(str(request.headers))}```"
    try:
        post_to_discord(content=message.content, name=message.name)
        return {"status": "ok"}
    except HTTPError as e:
        for _ in range(3):
            sleep(5)
            try:
                post_to_discord(content=message.content, name=message.name)
                return {"status": "ok"}
            except HTTPError:
                continue
        return {"status": "error", "detail": str(e)}
        

def main() -> None:
    import uvicorn

    production: bool = environ.get('PRODUCTION', 'false').lower() == 'true'
    if production:
        uvicorn.run('api.main:app', host='0.0.0.0', port=8000, workers=4)
    else:
        uvicorn.run('api.main:app', host='0.0.0.0', port=8000, reload=True)

if __name__ == '__main__':
    main()